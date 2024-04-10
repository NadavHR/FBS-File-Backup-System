import flet
from flet_core import border_radius, border

import call_endpoints
from app_layout import AppLayout
from appproject import AppProject
from data_store import DataStore
from flet import (
    AlertDialog,
    AppBar,
    Column,
    Container,
    ElevatedButton,
    Icon,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    RoundedRectangleBorder,
    Row,
    TemplateRoute,
    Text,
    TextField,
    UserControl,
    View,
    colors,
    icons,
    margin,
    padding,
    theme,
    Checkbox,
)
from memory_store import InMemoryStore
from app_user import User
from app_consts import *


class ClientApp(UserControl):
    def __init__(self, page: Page, store_own: DataStore, store_shared: DataStore):
        super().__init__()
        self.page = page
        self.own_projects_store: DataStore = store_own
        self.shared_projects_store: DataStore = store_shared
        self.page.on_route_change = self.route_change
        self.boards = self.own_projects_store.get_projects()
        self.user = ""
        self.login_profile_button = PopupMenuItem(text="Log in", on_click=self.login_popup)
        self.sign_up_button = PopupMenuItem(text="Sign up", on_click=self.sign_up)
        self.delete_profile_button = PopupMenuItem(
                text="Delete Profile",
                on_click=self.delete_profile
            )
        self.appbar_items = [
            self.login_profile_button,
            PopupMenuItem(),  # divider
            self.sign_up_button,
        ]
        self.appbar = AppBar(
            leading=Icon(icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=Text(f"FBS", font_family="Pacifico", size=32, text_align="start"),
            center_title=False,
            toolbar_height=75,
            bgcolor=colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                Container(
                    content=PopupMenuButton(items=self.appbar_items),
                    margin=margin.only(left=50, right=25),
                )
            ],
        )
        self.page.appbar = self.appbar
        self.page.update()

    def build(self):
        self.layout = AppLayout(
            self,
            self.page,
            self.own_projects_store,
            self.shared_projects_store,
            tight=True,
            expand=True,
            vertical_alignment="start",
        )
        return self.layout

    def initialize(self):
        # self.page.views.clear()
        self.page.views.append(
            View(
                "/",
                [self.appbar, self.layout],
                padding=padding.all(0),
                bgcolor=colors.BLUE_GREY_900,
            )
        )
        self.page.update()
        try:
            call_endpoints.logout(call_endpoints.get_cached_session_id())
        except:
            pass
        # create an initial board for demonstration if no boards
        # if len(self.boards) == 0:
        #     self.create_new_board("My First Board")
        self.page.go("/")

    def sign_up(self, e):
        def close_dlg(e):
            session_id = call_endpoints.get_cached_session_id()
            if not (session_id is None):
                call_endpoints.logout(session_id)
            if user_name.value == "":
                user_name.error_text = "Please provide username"
                self.page.update()
                return
            user_name.error_text = ""
            if password.value == "":
                password.error_text = "Please provide password"
                self.page.update()
                return
            user = User(user_name.value, password.value)
            ok, message = call_endpoints.sign_up(user.name, user.password)
            if not ok:
                user_name.error_text = message
                password.error_text = message
                self.page.update()
                return
            else:
                if user not in self.own_projects_store.get_users():
                    self.own_projects_store.add_user(user)
                self.user = user_name.value
                self.page.client_storage.set("current_user", user_name.value)

            dialog.open = False
            self.appbar_items[0] = PopupMenuItem(
                text=f"{self.page.client_storage.get('current_user')}'s Profile",
                on_click=self.logout_popup
            )
            self.appbar_items[2] = PopupMenuItem(
                text="Delete Profile",
                on_click=self.delete_profile
            )
            self.update_projects()
            self.page.update()

        user_name = TextField(label="User name", on_submit=close_dlg)
        password = TextField(label="Password", password=True, on_submit=close_dlg)
        dialog = AlertDialog(
            title=Text("Sign up"),
            content=Column(
                [
                    user_name,
                    password,
                    ElevatedButton(text="Sign up", on_click=close_dlg),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def login_popup(self, e):
        def close_dlg(e):
            session_id = call_endpoints.get_cached_session_id()
            if not (session_id is None):
                call_endpoints.logout(session_id)
            if user_name.value == "":
                user_name.error_text = "Please provide username"
                self.page.update()
                return
            user_name.error_text = ""
            if password.value == "":
                password.error_text = "Please provide password"
                self.page.update()
                return
            user = User(user_name.value, password.value)
            ok, message = user.login()
            if not ok:
                user_name.error_text = message
                password.error_text = message
                self.page.update()
                return
            else:
                if user not in self.own_projects_store.get_users():
                    self.own_projects_store.add_user(user)
                self.user = user_name.value
                self.page.client_storage.set("current_user", user_name.value)

            dialog.open = False
            self.appbar_items[0] = PopupMenuItem(
                text=f"{self.page.client_storage.get('current_user')}'s Profile",
                on_click=self.logout_popup
            )
            self.appbar_items[2] = self.delete_profile_button
            self.update_projects()
            self.page.update()

        user_name = TextField(label="User name", on_submit=close_dlg)
        password = TextField(label="Password", password=True, on_submit=close_dlg)
        dialog = AlertDialog(
            title=Text("Please enter your login credentials"),
            content=Column(
                [
                    user_name,
                    password,
                    ElevatedButton(text="Login", on_click=close_dlg),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_profile(self, e):
        def close_dlg(e):
            dialog.open = False
            ok, msg = call_endpoints.delete_user(call_endpoints.current_session_id)
            self.logout()
            # self.update()
            # self.pop_error(msg)

        def close(e):
            dialog.open = False
            self.update()
            self.page.update()

        dialog = AlertDialog(
            title=Text("are you sure you want to deactivate account?"),
            content=Column(
                [
                    ElevatedButton(text="close", on_click=close),
                    ElevatedButton(text="Deactivate", on_click=close_dlg, color=colors.RED_ACCENT),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def logout_popup(self, e):
        def close_dlg(e):
            dialog.open = False
            self.logout()

        dialog = AlertDialog(
            title=Text("are you sure you want to Logout?"),
            content=Column(
                [
                    ElevatedButton(text="Logout", on_click=close_dlg),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def logout(self):
        call_endpoints.logout(call_endpoints.current_session_id)
        call_endpoints.cache_session_id(None)
        self.appbar_items[0] = self.login_profile_button
        self.appbar_items[2] = self.sign_up_button
        self.update_projects()
        self.layout.hydrate_all_projects_view()
        self.layout.active_view.update()
        self.update()
        self.page.update()

    def route_change(self, e):
        troute = TemplateRoute(self.page.route)
        if troute.match("/"):
            self.page.go("/Projects")
        elif troute.match("/board/:id"):
            if int(troute.id) > len(self.own_projects_store.get_projects()):
                self.page.go("/")
                return
            self.layout.set_board_view(int(troute.id))
        elif troute.match("/Projects"):
            self.layout.set_projects_view()
        elif troute.match("/Shared"):
            self.layout.set_shared_view()
        self.page.update()

    def pop_error(self, error: str):
        def close(e):
            dialog.open = False
            self.page.update()
        dialog = AlertDialog(title=Text(error))
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


    def add_project(self, e):
        def submit_data(e):
            ok, msg = call_endpoints.add_project(call_endpoints.current_session_id, name_field.value, desc_field.value)
            if ok:
                if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (
                        type(e.control) is TextField and e.control.value != ""
                ):
                    self.create_new_project(name_field.value)
                dialog.open = False
            else:
                name_field.error_text = msg
                desc_field.error_text = msg
                dialog.open = True
            self.page.update()

        def close(e):
            dialog.open = False
            self.page.update()

        def textfield_change(e):
            if name_field.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()

        name_field = TextField(
            label="New Project Name", on_submit=submit_data, on_change=textfield_change
        )
        desc_field = TextField(
            label="New Project Description", on_submit=submit_data
        )
        create_button = ElevatedButton(
            text="Create", bgcolor=colors.BLUE_400, on_click=submit_data, disabled=True
        )
        if not (call_endpoints.current_session_id is None):
            dialog = AlertDialog(
                title=Text("Create new Project"),
                content=Column(
                    [
                        name_field,
                        desc_field,
                        Row(
                            [
                                ElevatedButton(text="Cancel", on_click=close),
                                create_button,
                            ],
                            alignment="spaceBetween",
                        ),
                    ],
                    tight=True,
                ),
                on_dismiss=lambda e: print("Modal dialog dismissed!"),
            )
        else:
            dialog = AlertDialog(title=Text("log in to create projects"))
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        name_field.focus()

    def create_new_project(self, project_name):
        new_project = AppProject(self, self.own_projects_store, project_name, self.user)
        self.own_projects_store.add_project(new_project)
        self.layout.hydrate_all_projects_view()

    def _add_shared_project(self, project_name, owner):
        new_project = AppProject(self, self.shared_projects_store, project_name, owner)
        self.shared_projects_store.add_project(new_project)
        self.layout.hydrate_all_projects_view()

    def delete_project(self, e):
        call_endpoints.delete_project(call_endpoints.current_session_id,
                                      e.control.content.data.name)
        self.own_projects_store.remove_project(e.control.content.data)
        self.layout.set_projects_view()
        self.update_projects()

    def check_project_info(self, e):
        project_name = e.control.content.data.name

        def close(e):
            dialog.open = False
            self.page.update()

        ok, msg = call_endpoints.get_project_info(call_endpoints.current_session_id,
                                                  project_name,
                                                  e.control.content.data.owner_name)
        if ok:
            dialog = AlertDialog(
                title=Text(f"check info on {project_name}"),
                content=Column(
                    [
                        Text(f"description: {msg[DESCRIPTION_FIELD]}"),
                        Text(f"project owner: {e.control.content.data.owner_name}"),
                        Text(f"project created at {msg[TIME_FIELD]}"),
                        Text(f"this project has {msg[COMMIT_COUNT_FIELD]} commits"),
                        Text("\npermissions: "),
                        Container(
                            content=Column([
                                Row([
                                    Text(access[0]),
                                    Text("Write" if access[1] else "ReadOnly", color=colors.GREEN_ACCENT)
                                ])
                                for access in msg[SHARED_WITH_FIELD]
                            ]
                            ),
                            border_radius=border_radius.all(5),
                            border=border.all(3, colors.BLUE_GREY_700),
                            bgcolor=colors.BLUE_GREY_700,
                            padding=padding.all(10),
                            width=250,
                        ),
                        Row(
                            [
                                ElevatedButton(text="Cancel", on_click=close),
                            ],
                            alignment="spaceBetween",
                        ),
                    ],
                    tight=True,
                ),
                on_dismiss=lambda e: print("Modal dialog dismissed!"),
            )
        else:
            dialog = AlertDialog(
                title=Text(f"check info on {project_name}"),
                content=Column(
                    [
                        Text(f"Error: {msg}", color=colors.RED_ACCENT),
                        Row(
                            [
                                ElevatedButton(text="Cancel", on_click=close),
                            ],
                            alignment="spaceBetween",
                        ),
                    ],
                    tight=True,
                ),
                on_dismiss=lambda e: print("Modal dialog dismissed!"),
            )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def change_project_share(self, e):
        project_name = e.control.content.data.name
        name_field = TextField(label="user to share with")
        write = Checkbox(label="Write Access", width=200)

        def submit_data(e):
            if name_field.value == "":
                name_field.error_text = "please enter name"
                self.page.update()
                return
            ok, msg = call_endpoints.update_project_sharing(call_endpoints.current_session_id, project_name,
                                                            name_field.value, write.value)
            if ok:
                close(e)
                return
            name_field.error_text = msg
            self.page.update()

        def delete_access(e):
            if name_field.value == "":
                name_field.error_text = "please enter name"
                self.page.update()
                return
            ok, msg = call_endpoints.update_project_sharing(call_endpoints.current_session_id, project_name,
                                                            name_field.value)
            if ok:
                close(e)
                return
            name_field.error_text = msg
            self.page.update()

        def close(e):
            dialog.open = False
            self.page.update()

        share_button = ElevatedButton(text="update sharing", bgcolor=colors.BLUE_400, on_click=submit_data)
        delete_access_button = ElevatedButton(text="Delete access to user", bgcolor=colors.RED_ACCENT,
                                              on_click=delete_access)
        dialog = AlertDialog(
            title=Text(f"change access to {project_name}"),
            content=Column(
                [
                    Column(
                        [
                            name_field,
                            write
                        ]
                    ),
                    Row(
                        [
                            ElevatedButton(text="Cancel", on_click=close),
                            share_button,
                            delete_access_button
                        ],
                        alignment="spaceBetween",
                    ),
                ],
                tight=True,
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def update_projects(self):
        for project in self.own_projects_store.get_projects():
            self.own_projects_store.remove_project(project)
        for project in self.shared_projects_store.get_projects():
            self.shared_projects_store.remove_project(project)
        # self.layout.set_projects_view()
        if not (call_endpoints.get_cached_session_id() is None):
            ok, projects = call_endpoints.get_user_projects(call_endpoints.current_session_id)
            if ok:
                for project in projects[OWN_PROJECTS_FIELD]:
                    self.create_new_project(project)
                for name in projects[SHARED_PROJECTS_FIELD]:
                    for project in projects[SHARED_PROJECTS_FIELD][name]:
                        self._add_shared_project(project, name)
            elif projects == SESSION_EXPIRED_MESSAGE:
                self.logout()
        # self.layout.hydrate_all_projects_view()
        self.page.update()


def main(page: Page):
    page.title = "FBS"
    page.padding = 0
    page.theme = theme.Theme(font_family="Verdana")
    page.theme.page_transitions.windows = "cupertino"
    page.bgcolor = colors.BLUE_GREY_900
    app = ClientApp(page, InMemoryStore(), InMemoryStore())
    page.add(app)
    page.update()
    app.initialize()


flet.app(target=main)
