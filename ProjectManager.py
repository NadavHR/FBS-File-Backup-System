import os

import constants
from ProjectClass import Project
from Response import Response
from Commit import Commit

class ProjectManager(constants.Constants):

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
        if target_project.user_name == user:
            return True
        if write:
            return os.path.isfile(
                f"{target_project.path_to_permissions()}\\{user}\\{Project.WRITE_PERMISSION_FILE_NAME}")
        else:
            return os.path.isdir(f"{target_project.path_to_permissions()}\\{user}")

    @staticmethod
    def is_user(user_name: str) -> bool:
        """
        checks if a user exists
        :param user_name: the username to check
        :return: true if the user exists, false if not
        """
        return os.path.isdir(Project.USERS_DIR + "\\" + user_name)

    @staticmethod
    def _list_projects(user_name: str) -> list[Project]:
        """
        lists all of the projects a user has, DOES NOT CHECK IF THE USER EXISTS
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
    def get_user_projects(user_name: str) -> Response:
        """
        lists a users projects, REMEMBER TO MAKE SURE THE USER CHECKING IS THE USER BEING CHECKED
        :param user_name: the user we want to check
        :return: a response with all of the projects in the response message
        """
        if not ProjectManager.is_user(user_name):
            return ProjectManager.E_USER_DOESNT_EXIST
        projects = [a.project_name for a in ProjectManager._list_projects(user_name)]
        return Response(success=True, response_message=projects)

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

        if not ProjectManager.is_user(project.user_name):  # makes sure the user exists
            return ProjectManager.E_USER_DOESNT_EXIST

        if ProjectManager._count_projects(project.user_name) == ProjectManager.USER_PROJECT_LIMIT:
            # checks if user exceeds project limit
            return ProjectManager.E_PROJECT_LIMIT_REACHED

        if project.exists():  # checks if the project exists
            return ProjectManager.E_PROJECT_ALREADY_EXISTS

        if not project.create():  # failed for some reason were not sure of
            return ProjectManager.E_UNKNOWN_ERROR

        return ProjectManager.S_PROJECT_CREATED

    @staticmethod
    def update_project_permissions(user: str, project: Project, write: bool = None) -> Response:
        """
        updates the permissions of a user MAKE SURE WHO EVER SUBMITTED THE REQUEST IS QUALIFIED TO DO IT!!!
        :param user: the user who's permissions we want to update
        :param project: the project who's permissions we want to update
        :param write: the access we want to grant (True for write, False for readonly, None to delete access)
        :return: the response to the request
        """
        # TODO: add a way to make sure a user knows all projects he'd been given access to
        if not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST

        if not ProjectManager.is_user(user):
            return ProjectManager.E_USER_DOESNT_EXIST

        if project.user_name == user:
            return ProjectManager.E_CANT_CHANGE_OWNER_ACCESS
        # deletes permissions for users who no longer exist
        perms = project.list_permission()
        for p in perms:
            if not ProjectManager.is_user(p[0]):
                project.delete_permission(p[0])
        perms = project.list_permission()
        if len(perms) == ProjectManager.PROJECT_SHARING_LIMIT:
            return ProjectManager.E_PROJECT_SHARE_LIMIT_REACHED

        if not (write is None):
            project.give_permissions(user, write)
        elif user in [a[0] for a in perms]:
            project.delete_permission(user)
        else:
            return ProjectManager.E_CANT_DELETE_NON_EXISTENT_ACCESS

        return ProjectManager.S_ACCESS_GRANTED

    @staticmethod
    def commit_to(project: Project, commit: Commit) -> Response:
        """
        this method commits a new commit to a given project (if possible)
        :param project: the project being commited to
        :param commit: the commit we are trying to commit to the project
        :return: a Response object with the fitting response message
        """
        if not ProjectManager.is_user(commit.user):
            return ProjectManager.E_USER_DOESNT_EXIST
        elif not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST
        elif not ProjectManager.authenticate_permissions(user=commit.user, target_project=project, write=True):
            return ProjectManager.E_BAD_PERMISSIONS
        elif len(commit.data) > ProjectManager.COMMIT_SIZE_LIMIT:
            return ProjectManager.E_BAD_COMMIT_SIZE
        elif project.count_commits() > Project.COMMIT_LIMIT:
            return ProjectManager.E_COMMIT_LIMIT_REACHED
        elif not commit.commit():
            return ProjectManager.E_UNKNOWN_ERROR
        return ProjectManager.S_COMMIT_SUCCESSFUL

    @staticmethod
    def delete_project(project: Project):
        """
        deletes a project, ONLY USE IF THE USER WHO ASKS FOR DELETION IS THE OWNER
        :param project: the project we want to delete
        :return: Response object
        """
        if project.delete():
            return ProjectManager.S_PROJECT_DELETED
        else:
            return ProjectManager.E_PROJECT_DOESNT_EXIST
