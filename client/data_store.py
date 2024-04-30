from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_project import AppProject
    from app_commit import AppCommit
    from user import User


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

    def add_commit(self, board, model) -> None:
        raise NotImplementedError

    def get_lists(self) -> list["AppCommit"]:
        raise NotImplementedError

    def get_list(self, id) -> "AppCommit":
        raise NotImplementedError

    def get_commits_by_project(self, board) -> list["AppCommit"]:
        raise NotImplementedError

    def remove_commit(self, board, id) -> None:
        raise NotImplementedError
