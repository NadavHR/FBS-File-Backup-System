from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_project import AppProject
    from app_commit import AppCommit
    from user import User
from data_store import DataStore


class InMemoryStore(DataStore):
    def __init__(self):
        self.projects: dict[int, "AppProject"] = {}
        self.users: dict[str, "User"] = {}
        self.commits: dict[int, list["AppCommit"]] = {}

    def add_project(self, board: "AppProject"):
        self.projects[board.project_id] = board

    def get_project(self, id: int):
        return self.projects[id]

    def update_project(self, board: "AppProject", update: dict):
        for k in update:
            setattr(board, k, update[k])

    def get_projects(self):
        return [self.projects[b] for b in self.projects]

    def remove_project(self, board: "AppProject"):
        del self.projects[board.project_id]
        self.commits[board.project_id] = []

    def add_commit(self, board: int, commit: "AppCommit"):
        if board in self.commits:
            self.commits[board].append(commit)
        else:
            self.commits[board] = [commit]

    def get_commits_by_project(self, board: int):
        return self.commits.get(board, [])

    def remove_commit(self, board: int, id: int):
        self.commits[board] = [
            l for l in self.commits[board] if not l.commit_id == id]

    def add_user(self, user: "User"):
        self.users[user.name] = user

    def get_users(self):
        return [self.users[u] for u in self.users]