import flet
import call_endpoints
from app_layout import AppLayout
from board import Board
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
)
from memory_store import InMemoryStore
from app_user import User

SHARED_PROJECTS_FIELD = "shared"
OWN_PROJECTS_FIELD = "projects"
SESSION_EXPIRED_MESSAGE = "expired or illegal session ID"
class ClientApp(UserControl):
    def __init__(self, page: Page, store: DataStore):
        super().__init__()
        self.page = page
        self.store: DataStore = store
        self.page.on_route_change = self.route_change
        self.boards = self.store.get_boards()
        self.login_profile_button = PopupMenuItem(text="Log in", on_click=self.login_popup)
        self.appbar_items = [
            self.login_profile_button,
            PopupMenuItem(),  # divider
            PopupMenuItem(text="Settings"),
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
            self.store,
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
        # create an initial board for demonstration if no boards
        # if len(self.boards) == 0:
        #     self.create_new_board("My First Board")
        self.page.go("/")

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
                if user not in self.store.get_users():
                    self.store.add_user(user)
                self.user = user_name.value
                self.page.client_storage.set("current_user", user_name.value)

            dialog.open = False
            self.appbar_items[0] = PopupMenuItem(
                text=f"{self.page.client_storage.get('current_user')}'s Profile",
                on_click=self.logout_popup
            )
            self.update_projects()
            self.page.update()

        user_name = TextField(label="User name")
        password = TextField(label="Password", password=True)
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
        self.update_projects()



    def route_change(self, e):
        troute = TemplateRoute(self.page.route)
        if troute.match("/"):
            self.page.go("/boards")
        elif troute.match("/board/:id"):
            if int(troute.id) > len(self.store.get_boards()):
                self.page.go("/")
                return
            self.layout.set_board_view(int(troute.id))
        elif troute.match("/boards"):
            self.layout.set_all_boards_view()
        elif troute.match("/members"):
            self.layout.set_members_view()
        self.page.update()

    def add_board(self, e):
        def submit_data(e):
            ok, msg = call_endpoints.add_project(call_endpoints.current_session_id, name_field.value, desc_field.value)
            if ok:
                if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (
                    type(e.control) is TextField and e.control.value != ""
                ):
                    self.create_new_board(name_field.value)
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
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        name_field.focus()

    def create_new_board(self, board_name):
        new_board = Board(self, self.store, board_name)
        self.store.add_board(new_board)
        self.layout.hydrate_all_boards_view()

    def delete_board(self, e):
        call_endpoints.delete_project(call_endpoints.current_session_id,
                                      e.control.content.data.name)
        self.store.remove_board(e.control.content.data)
        self.layout.set_all_boards_view()
        self.update_projects()

    def update_projects(self):
        for project in self.store.get_boards():
            self.store.remove_board(project)
            self.layout.set_all_boards_view()
        if not (call_endpoints.get_cached_session_id() is None):
            ok, projects = call_endpoints.get_user_projects(call_endpoints.current_session_id)
            if ok:
                for name in projects[OWN_PROJECTS_FIELD]:
                    self.create_new_board(name)
            elif projects == SESSION_EXPIRED_MESSAGE:
                self.logout()
        self.layout.hydrate_all_boards_view()
        self.page.update()


def main(page: Page):

    page.title = "FBS"
    page.padding = 0
    page.theme = theme.Theme(font_family="Verdana")
    page.theme.page_transitions.windows = "cupertino"
    page.bgcolor = colors.BLUE_GREY_900
    app = ClientApp(page, InMemoryStore())
    page.add(app)
    page.update()
    app.initialize()



flet.app(target=main)
