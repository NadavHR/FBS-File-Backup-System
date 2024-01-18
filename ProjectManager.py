import os
from ProjectClass import Project
from Response import Response


class ProjectManager:
    USER_PROJECT_LIMIT = 8
    PROJECT_SHARING_LIMIT = 32

    def __init__(self):
        pass

    @staticmethod
    def authenticate_permissions(user: str, target_project: Project, write: bool) -> bool:
        """
        this method checks if a user has permission to perform a certain action (write or read only)
        :param target_project: the target project we want to check permissions to
        :param user: the name of the user who's trying to perform the action
        :param write: True if we ask for an action requiring write permissions, False for readonly
        :return: True if the user has permissions to perform that action, False otherwise
        """
        if write:
            return os.path.isfile(f"{target_project.path_to_permissions()}\\{user}\\{Project.WRITE_PERMISSION_FILE_NAME}")
        else:
            return os.path.isdir(f"{target_project.path_to_permissions()}\\{user}")

    @staticmethod
    def is_user(user_name: str) -> bool:
        """
        checks if a user exists
        :param user_name: the username to check
        :return: true if the user exists, false if not
        """
        return os.path.isdir(ProjectManager.USERS_DIR + "\\" + user_name)

    @staticmethod
    def _list_projects(user_name: str) -> list[Project]:
        """
        lists all of the projects a user has
        :param user_name: the user we want to check
        :return: a list of every name of a project the user has
        """
        projects = []
        dir_path = f"{Project.USERS_DIR}\\{user_name}\\{Project.PROJECTS_DIR}"
        for path in os.listdir(dir_path):
            # check if current path is a file
            if not os.path.isfile(os.path.join(dir_path, path)):
                projects.append(Project(user_name=user_name, project_name=path))
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
    def add_project(project: Project) -> Response:
        """
        add a project to a user (if possible)
        :param project: the project were trying to create
        :return: the response to the request
        """
        resp = Response()
        resp.success = False

        if not ProjectManager.is_user(project.user_name):  # makes sure the user exists
            resp.response_message = "user does not exist"
            return resp

        if project.exists():  # checks if the project exists
            resp.response_message = "project already exists"
            return resp

        if ProjectManager._count_projects(project.user_name) == ProjectManager.USER_PROJECT_LIMIT:
            # checks if user exceeds project limit
            resp.response_message = "user at project amount limit"
            return resp

        os.mkdir(project.to_path())
        resp.success = True
        resp.response_message = f"successfully created project {project.user_name}\\{project.project_name}"

        return resp

    @staticmethod
    def update_project_permissions(user: str, project: Project, write: bool) -> Response:
        """
        updates the permissions of a user MAKE SURE WHO EVER SUBMITTED THE REQUEST IS QUALIFIED TO DO IT!!!
        :param user: the user who's permissions we want to update
        :param project: the project whos permissions we want to update
        :param write: the access we want to grant (True for write, False for readonly)
        :return: the response to the request
        """
        resp = Response()
        resp.success = False
        if not project.exists():
            resp.response_message = "the project does not exist"
            return resp

        # deletes permissions for users who no longer exist
        perms = project.list_permission()
        for p in perms:
            if not ProjectManager.is_user(p[0]):
                project.delete_permission(p[0])

        if len(project.list_permission()) == ProjectManager.PROJECT_SHARING_LIMIT:
            resp.response_message = "can not share project with any more users"
            return resp

        project.give_permissions(user, write)
        resp.response_message(f"successfully granted access to user {user}")
        return resp

