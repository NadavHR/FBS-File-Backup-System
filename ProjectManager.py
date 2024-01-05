import os

from Response import Response


class ProjectManager:
    USERS_DIR = "users"
    PROJECTS_DIR = "projects"
    # to access a project {USERS_DIR}\{user_name}\{PROJECTS_DIR}\{project_name}
    USER_PROJECT_LIMIT = 8

    def __init__(self):
        pass

    @staticmethod
    def is_user(user_name: str) -> bool:
        """
        checks if a user exists
        :param user_name: the username to check
        :return: true if the user exists, false if not
        """
        return os.path.isdir(ProjectManager.USERS_DIR + "\\" + user_name)

    @staticmethod
    def is_project(user_name: str, project_name: str) -> bool:
        """
        checks if a project exists
        :param user_name: the name of the user who owns the project
        :param project_name: the name of the project we want to check
        :return: True if project exists False otherwise
        """
        return os.path.isdir(f"{ProjectManager.USERS_DIR}\\{user_name}\\{ProjectManager.PROJECTS_DIR}\\{project_name}")

    @staticmethod
    def _list_projects(user_name: str) -> list[str]:
        """
        lists all of the projects a user has
        :param user_name: the user we want to check
        :return: a list of every name of a project the user has
        """
        projects = []
        dir_path = f"{ProjectManager.USERS_DIR}\\{user_name}\\{ProjectManager.PROJECTS_DIR}"
        for path in os.listdir(dir_path):
            # check if current path is a file
            if not os.path.isfile(os.path.join(dir_path, path)):
                projects.append(path)
        return projects

    @staticmethod
    def _count_projects(user_name: str) -> int:
        """
        counts how many projects a user has
        :param user_name: the name of the user we want to check
        :return: the amount of projects a user has
        """
        return len(ProjectManager._list_projects(user_name))

    @staticmethod
    def add_project(user_name: str, project_name: str) -> Response:
        """
        add a project to a user (if possible)
        :param user_name: the name of the user where we want to add the user
        :param project_name: the name of the project you want to add
        :return: the response to the request
        """
        resp = Response()
        resp.success = False

        if not ProjectManager.is_user(user_name):  # makes sure the user exists
            resp.response_message = "user does not exist"
            return resp

        if ProjectManager.is_project(user_name, project_name):  # checks if the project exists
            resp.response_message = "project already exists"
            return resp

        if ProjectManager._count_projects(user_name) == ProjectManager.USER_PROJECT_LIMIT:
            # checks if user exceeds project limit
            resp.response_message = "user at project amount limit"
            return resp

        os.mkdir(f"{ProjectManager.USERS_DIR}\\{user_name}\\{ProjectManager.PROJECTS_DIR}\\{project_name}")
        resp.success = True
        resp.response_message = f"successfully created project {user_name}\\{project_name}"

        return resp
