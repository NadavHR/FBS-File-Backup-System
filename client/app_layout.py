from appproject import AppProject
import call_endpoints
from data_store import DataStore
from flet import (
    ButtonStyle,
    Column,
    Container,
    Control,
    IconButton,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    RoundedRectangleBorder,
    Row,
    Text,
    TextButton,
    TextField,
    border,
    border_radius,
    colors,
    icons,
    padding,
)
from sidebar import Sidebar


class AppLayout(Row):
    def __init__(self, app, page: Page, store_own: DataStore, store_shared: DataStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.page = page
        self.page.on_resize = self.page_resize
        self.store_own: DataStore = store_own
        self.store_shared = store_shared
        self.toggle_nav_rail_button = IconButton(
            icon=icons.ARROW_CIRCLE_LEFT,
            icon_color=colors.BLUE_GREY_400,
            selected=False,
            selected_icon=icons.ARROW_CIRCLE_RIGHT,
            on_click=self.toggle_nav_rail,
        )
        self.sidebar = Sidebar(self, self.store_own, page)
        self.login_for_projects_message = Row([Text("log in to view projects")])
        self.no_projects_message = Row([Text("No Projects to Display")])
        self.shared_view = Column(
            [
                Row(
                    [
                        Container(
                            Text(value="Shared Projects", style="headlineMedium"),
                            expand=True,
                            padding=padding.only(top=15),
                        ),
                    ]
                ),
                # Row(
                #     [
                #         TextField(
                #             hint_text="Search all Projects",
                #             autofocus=False,
                #             content_padding=padding.only(left=10),
                #             width=200,
                #             height=40,
                #             text_size=12,
                #             border_color=colors.BLACK26,
                #             focused_border_color=colors.BLUE_ACCENT,
                #             suffix_icon=icons.SEARCH,
                #         )
                #     ]
                # ),
                self.login_for_projects_message,
            ],
            expand=True,
        )
        #Text("Shared Projects")
        self.projects_view = Column(
            [
                Row(
                    [
                        Container(
                            Text(value="Your Projects", style="headlineMedium"),
                            expand=True,
                            padding=padding.only(top=15),
                        ),
                        Container(
                            TextButton(
                                "Add new Project",
                                icon=icons.ADD,
                                on_click=self.app.add_project,
                                style=ButtonStyle(
                                    bgcolor={
                                        "": colors.BLUE_GREY_600,
                                        "hovered": colors.BLUE_900,
                                    },
                                    shape={"": RoundedRectangleBorder(radius=3)},
                                ),
                            ),
                            padding=padding.only(right=50, top=15),
                        ),
                    ]
                ),
                # Row(
                #     [
                #         TextField(
                #             hint_text="Search all Projects",
                #             autofocus=False,
                #             content_padding=padding.only(left=10),
                #             width=200,
                #             height=40,
                #             text_size=12,
                #             border_color=colors.BLACK26,
                #             focused_border_color=colors.BLUE_ACCENT,
                #             suffix_icon=icons.SEARCH,
                #         )
                #     ]
                # ),
                self.login_for_projects_message,
            ],
            expand=True,
        )
        self._active_view: Control = self.projects_view

        self.controls = [self.sidebar, self.toggle_nav_rail_button, self.active_view]

    @property
    def active_view(self):
        return self._active_view

    @active_view.setter
    def active_view(self, view):
        self._active_view = view
        self.controls[-1] = self._active_view
        self.sidebar.sync_board_destinations()
        self.update()

    def set_board_view(self, i):
        self.active_view = self.store_own.get_projects()[i]
        self.sidebar.bottom_nav_rail.selected_index = i
        self.sidebar.top_nav_rail.selected_index = None
        self.sidebar.update()
        self.page.update()
        self.page_resize()

    def set_projects_view(self):
        self.active_view = self.projects_view
        self.app.update_projects()
        self.hydrate_all_projects_view()
        self.sidebar.top_nav_rail.selected_index = 0
        self.sidebar.bottom_nav_rail.selected_index = None
        self.sidebar.update()
        self.update()
        self.page.update()

    def set_shared_view(self):
        self.active_view = self.shared_view
        self.app.update_projects()
        self.sidebar.top_nav_rail.selected_index = 1
        self.sidebar.bottom_nav_rail.selected_index = None
        self.sidebar.update()
        self.page.update()

    def page_resize(self, e=None):
        if type(self.active_view) is AppProject:
            self.active_view.resize(
                self.sidebar.visible, self.page.width, self.page.height
            )
        self.page.update()

    def hydrate_all_projects_view(self):
        self.projects_view.controls[-1] = Row(
            [
                Container(
                    content=Row(
                        [
                            Container(
                                content=Text(value=b.name),
                                data=b,
                                expand=True,
                                on_click=self.board_click,
                            ),
                            Container(
                                content=PopupMenuButton(
                                    items=[
                                        PopupMenuItem(
                                            content=Text(
                                                value="Delete",
                                                style="labelMedium",
                                                text_align="center",
                                                data=b,
                                            ),

                                            on_click=self.app.delete_project,

                                        ),
                                        PopupMenuItem(
                                            content=Text(
                                                value="Change Share Settings",
                                                style="labelMedium",
                                                text_align="center",
                                                data=b,
                                            ),

                                            on_click=self.app.change_project_share,
                                        ),
                                        PopupMenuItem(
                                            content=Text(
                                                value="Check Info",
                                                style="labelMedium",
                                                text_align="center",
                                                data=b,
                                            ),
                                            on_click=self.app.check_project_info,
                                        ),
                                    ]
                                ),
                                padding=padding.only(right=-10),
                                border_radius=border_radius.all(3),
                            ),
                        ],
                        alignment="spaceBetween",
                    ),
                    border=border.all(1, colors.BLACK38),
                    border_radius=border_radius.all(5),
                    bgcolor=colors.BLUE_GREY_400,
                    padding=padding.all(10),
                    width=250,
                    data=b,
                )
                for b in self.store_own.get_projects()
            ],
            wrap=True,
        )
        self.shared_view.controls[-1] = Row(
            [
                Container(
                    content=Row(
                        [
                            Container(
                                content=Text(value=b.name),
                                data=b,
                                expand=True,
                                on_click=self.board_click,
                            ),
                            Container(
                                content=PopupMenuButton(
                                        items=[
                                            PopupMenuItem(
                                            content=Text(
                                                value="Check Info",
                                                style="labelMedium",
                                                text_align="center",
                                                data=b,
                                            ),
                                            on_click=self.app.check_project_info,
                                        ),
                                        ]
                                )
                            )
                        ],
                        alignment="spaceBetween",
                    ),
                    border=border.all(1, colors.BLACK38),
                    border_radius=border_radius.all(5),
                    bgcolor=colors.BLUE_GREY_400,
                    padding=padding.all(10),
                    width=250,
                    data=b,
                )
                for b in self.store_shared.get_projects()
            ],
            wrap=True,
        )

        if call_endpoints.current_session_id is None:
            self.projects_view.controls[-1] = self.login_for_projects_message
            self.shared_view.controls[-1] = self.login_for_projects_message
        else:
            if len(self.store_own.get_projects()) == 0:
                self.projects_view.controls[-1] = self.no_projects_message
            if len(self.store_shared.get_projects()) == 0:
                self.shared_view.controls[-1] = self.no_projects_message
        self.sidebar.sync_board_destinations()


    def board_click(self, e):
        self.sidebar.bottom_nav_change(self.store_own.get_projects().index(e.control.data))

    def toggle_nav_rail(self, e):
        self.sidebar.visible = not self.sidebar.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.page_resize()
        self.page.update()
