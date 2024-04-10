from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from appproject import AppProject
import itertools
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
                                content=Text(value="Move List", style="labelMedium",
                                             text_align="center", color=colors.WHITE))
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

    def delete_list(self, e):
        self.project.delete_commit(self, e)

    def edit_title(self, e):
        pass

    def save_title(self, e):
        pass

