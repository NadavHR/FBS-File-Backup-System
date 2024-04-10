from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from appproject import AppProject
import itertools
import call_endpoints
from flet import (
    UserControl,
    Draggable,
    DragTarget,
    Column,
    Row,
    Text,
    Icon,
    PopupMenuButton,
    PopupMenuItem,
    Container,
    TextButton,
    TextField,
    icons,
    border_radius,
    alignment,
    border,
    colors,
    padding,
)
from data_store import DataStore
from app_consts import *

class AppCommit(UserControl):
    id_counter = itertools.count()

    def __init__(self, project: "AppProject", store: DataStore, title: str, color: str = "", description: str = "",
                 commit_id: int = next(id_counter)):
        super().__init__()
        self.commit_id = commit_id
        self.store: DataStore = store
        self.project = project
        self.title = title
        self.description = description
        self.color = color

    def build(self):
        self.header = Row(
            controls=[
                Text(value=self.title, style="titleMedium",
                     text_align="left", overflow="clip", expand=True),
                Text(value=f"id: {self.commit_id}"),

                Container(
                    PopupMenuButton(
                        items=[
                            PopupMenuItem(
                                content=Text(value="Edit", style="labelMedium",
                                             text_align="center", color=colors.WHITE),
                                on_click=self.edit_title),
                            PopupMenuItem(),
                            PopupMenuItem(
                                content=Text(value="Delete", style="labelMedium",
                                             text_align="center", color=colors.WHITE),
                                on_click=self.delete_list),
                            PopupMenuItem(),
                            PopupMenuItem(
                                content=Text(value="Info", style="labelMedium",
                                             text_align="center", color=colors.WHITE,),
                                on_click=self.show_info),
                        ],
                    ),
                    padding=padding.only(right=-10)
                )
            ],
            alignment="spaceBetween"

        )

        self.inner_list = Container(
            content=Column([
                self.header,
                Text(self.description)

            ], spacing=4, tight=True, data=self.title),
            width=250,
            border=border.all(2, colors.BLACK12),
            border_radius=border_radius.all(5),
            bgcolor=self.color if (
                self.color != "") else colors.BACKGROUND,
            padding=padding.only(
                bottom=10, right=10, left=10, top=5)
        )
        self.view = DragTarget(
            content=self.inner_list,
            data=self,
        )

        return self.view

    def show_info(self, e):
        ok, msg = call_endpoints.get_commit_info(
            call_endpoints.current_session_id,
            self.project.name,
            self.project.owner_name,
            self.commit_id
        )
        if ok:
            msg = Column([
                Text(f"creation time: {msg[TIME_FIELD]}"),
                Text(f"created by {msg[COMMIT_USER_FIELD]}")
            ])
            self.project.app.pop_message(f"info on commit {self.title} ({self.commit_id})", msg)
        else:
            self.project.app.pop_error(msg)

    def delete_list(self, e):
        self.project.delete_commit(self, e)

    def edit_title(self, e):
        pass

    def save_title(self, e):
        pass

