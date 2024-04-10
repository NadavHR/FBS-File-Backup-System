import itertools
import os
import call_endpoints

from flet import (
    UserControl,
    Column,
    Row,
    FloatingActionButton,
    ElevatedButton,
    Text,
    GridView,
    Container,
    TextField,
    AlertDialog,
    Container,
    icons,
    border_radius,
    border,
    colors,
    padding,
    alignment,
    margin
)
from board_list import AppCommit
from data_store import DataStore
from app_consts import *

class AppProject(UserControl):
    id_counter = itertools.count()

    def __init__(self, app, store: DataStore, name: str, owner: str):
        super().__init__()
        self.board_id = next(AppProject.id_counter)
        self.store: DataStore = store
        self.app = app
        self.name = name
        self.owner_name = owner
        self.add_list_button = FloatingActionButton(
            icon=icons.ADD, text="new commit", height=30, on_click=self.create_list)

        self.board_lists = [
            self.add_list_button
        ]
        for l in self.store.get_lists_by_board(self.board_id):
            self.add_list(l)

        self.list_wrap = Column(
            self.board_lists,
            # vertical_alignment="start",
            visible=True,
            scroll="auto",
            width=(self.app.page.width - 310),
            height=(self.app.page.height - 95)
        )

    def build(self):
        self.view = Container(
            content=Column(
                controls=[
                    self.list_wrap
                ],

                scroll="auto",
                expand=True
            ),
            data=self,
            margin=margin.all(0),
            padding=padding.only(top=10, right=0),
            height=self.app.page.height,
        )
        return self.view

    def resize(self, nav_rail_extended, width, height):
        self.list_wrap.width = (
            width - 310) if nav_rail_extended else (width - 50)
        self.view.height = height
        self.list_wrap.update()
        self.view.update()

    def save_commit(self, commit_id: int):
        def close_dlg(e):
            save_button.disabled = True
            self.page.update()
            self.update()
            if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (type(e.control) is TextField and e.control.value != ""):
                if os.path.isdir(path_field.value):
                    ok, msg = call_endpoints.get_commit_data(call_endpoints.current_session_id,
                                                             self.name,
                                                             self.owner_name,
                                                             commit_id,
                                                             path_field.value)
                    if not ok:
                        self.app.pop_error(msg)
                    elif msg:
                        self.app.pop_error(f"Saved to {path_field.value}")

                    self.update_commits()
                    dialog.open = False
                else:
                    path_field.error_text = "not a valid path"
            self.page.update()
            self.update()

        def close(e):
            dialog.open = False
            self.page.update()
            self.update()

        def textfield_change(e):
            if path_field.value == "":
                save_button.disabled = True
            else:
                save_button.disabled = False
            self.page.update()
        path_field = TextField(label="Path to save to * ", on_submit=close_dlg, on_change=textfield_change)
        save_button = ElevatedButton(
            text="Save", bgcolor=colors.BLUE_400, on_click=close_dlg, disabled=True)
        dialog = AlertDialog(
            title=Text("Save to?"),
            content=Column([
                Container(content=Column(
                        [
                            path_field
                        ]),
                          padding=padding.symmetric(horizontal=5)),
                Row([
                    ElevatedButton(
                        text="Cancel", on_click=close),
                    save_button
                ], alignment="spaceBetween")
            ], tight=True, alignment="center"),

            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        name_field.focus()

    def create_list(self, e):
        def close_dlg(e):
            create_button.disabled = True
            self.page.update()
            self.update()
            if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (type(e.control) is TextField and e.control.value != ""):
                if os.path.isdir(path_field.value):
                    ok, msg = call_endpoints.commit(call_endpoints.current_session_id,
                                          self.name,
                                          self.owner_name,
                                          name_field.value,
                                          desc_field.value,
                                          path_field.value)
                    if not ok:
                        self.app.pop_error(msg)
                    self.update_commits()
                    dialog.open = False
                else:
                    path_field.error_text = "not a valid path"
            self.page.update()
            self.update()

        def close(e):
            dialog.open = False
            self.page.update()
            self.update()

        def textfield_change(e):
            if name_field.value == "" or path_field.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()
        name_field = TextField(label="New Commit Name * ",
                                on_submit=close_dlg, on_change=textfield_change)
        desc_field = TextField(label="Commit Description",
                                on_submit=close_dlg)
        path_field = TextField(label="Path to data * ", on_submit=close_dlg, on_change=textfield_change)
        create_button = ElevatedButton(
            text="Create", bgcolor=colors.BLUE_400, on_click=close_dlg, disabled=True)
        dialog = AlertDialog(
            title=Text("Name your Commit"),
            content=Column([
                Container(content=Column(
                        [
                            name_field,
                            desc_field,
                            path_field
                        ]),
                          padding=padding.symmetric(horizontal=5)),
                Row([
                    ElevatedButton(
                        text="Cancel", on_click=close),
                    create_button
                ], alignment="spaceBetween")
            ], tight=True, alignment="center"),

            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        name_field.focus()

    def remove_commit(self, commit: AppCommit, e):
        self.board_lists.remove(commit)
        self.store.remove_list(self.board_id, commit.commit_id)
        self.page.update()
        self.update()

    def delete_commit(self, commit: AppCommit, e):
        ok, msg = call_endpoints.delete_commit(call_endpoints.current_session_id, self.name, commit.commit_id)
        if not ok:
            self.app.pop_error(msg)
        self.update_commits()
        self.page.update()
        self.update()

    def add_list(self, list: AppCommit):
        self.board_lists.insert(1, list)
        self.store.add_list(self.board_id, list)

    def update_commits(self):
        for i in self.board_lists[1:]:
            self.remove_commit(i, None)
        ok, msg = call_endpoints.get_project_info(call_endpoints.current_session_id, self.name, self.owner_name)
        if ok:
            for i in range(msg[COMMIT_COUNT_FIELD]):
                ok, commit_info = call_endpoints.get_commit_info(
                    call_endpoints.current_session_id,
                    self.name,
                    self.owner_name,
                    i
                )
                if ok:
                    self.add_list(AppCommit(self,
                                            self.store,
                                            commit_info[COMMIT_NAME_FIELD],
                                            description=commit_info[COMMIT_MESSAGE_FIELD],
                                            commit_id=i), )
                else:
                    self.app.pop_error(commit_info)

        else:
            self.app.pop_error(msg)
        self.update()
