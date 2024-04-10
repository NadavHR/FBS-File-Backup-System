from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from appproject import AppProject
    from board_list import BoardList
    from user import User
    from item import Item


class DataStore:

    def add_project(self, model) -> None:
        raise NotImplementedError

    def get_project(self, id) -> "AppProject":
        raise NotImplementedError

    def get_projects(self) -> list["AppProject"]:
        raise NotImplementedError

    def update_project(self, model, update):
        raise NotImplementedError

    def remove_project(self, board) -> None:
        raise NotImplementedError

    def add_user(self, model) -> None:
        raise NotImplementedError

    def get_users(self) -> list["User"]:
        raise NotImplementedError

    def get_user(self, id) -> "User":
        raise NotImplementedError

    def remove_user(self, id) -> None:
        raise NotImplementedError

    def add_list(self, board, model) -> None:
        raise NotImplementedError

    def get_lists(self) -> list["BoardList"]:
        raise NotImplementedError

    def get_list(self, id) -> "BoardList":
        raise NotImplementedError

    def get_lists_by_board(self, board) -> list["BoardList"]:
        raise NotImplementedError

    def remove_list(self, board, id) -> None:
        raise NotImplementedError

    def add_item(self, board_list, model) -> None:
        raise NotImplementedError

    def get_items(self, board_list) -> list["Item"]:
        raise NotImplementedError

    def get_item(self, id) -> "Item":
        raise NotImplementedError

    def get_items_by_board(self, board) -> list["Item"]:
        raise NotImplementedError

    def remove_item(self, board_list, id) -> None:
        raise NotImplementedError