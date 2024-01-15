import os


class Project:
    USERS_DIR = "users"
    PROJECTS_DIR = "projects"
    # to access a project {USERS_DIR}\{user_name}\{PROJECTS_DIR}\{project_name}
    USER_SHARED_DIR = "shared"  # this dir contains a folder for every user who shares a project with this user and a
    # file named after the project for every project that user shares with the current user
    # to access shared projects {USERS_DIR}\{user_name}\{USER_SHARED_DIR}\{checked_user}\{checked_project}
    PROJECT_PERMISSIONS_DIR = "permissions"  # this dir contains a folder for every user with permissions and the folder
    # is either empty (meaning readonly permissions) or has an empty file meaning write permissions
    # to access permissions {path_to_project}\{PROJECT_PERMISSIONS_DIR}\{user_name}
    WRITE_PERMISSION_FILE_NAME = "W"
    # a user with write access {path_to_project}\{PROJECT_PERMISSIONS_DIR}\{user_name}\{WRITE_PERMISSION_FILE_NAME}

    def __init__(self, user_name: str, project_name: str):
        self.user_name = user_name
        self.project_name = project_name

    def path_to_permissions(self) -> str:
        """
        returns the path to the permissions directory of a project
        :return: the string of the path to the project
        """
        return f"{self.to_path()}\\{Project.PROJECT_PERMISSIONS_DIR}"

    def to_path(self) -> str:
        """
        returns the path to the project
        :return: a string of the path to the project
        """
        return f"{Project.USERS_DIR}\\{self.user_name}\\{Project.PROJECTS_DIR}\\{self.project_name}"

    def exists(self):
        """
        checks if this project exists
        :return: True if the project exists, false otherwise
        """
        return os.path.isdir(self.to_path())

    def list_permission(self) -> list[tuple[str, bool]]:
        # TODO: finish this
        """
        lists all of the permissions to the project
        :return: a list of tuples containing the name of the user and weather he has write access (True if he has)
        """
        dir_path = self.path_to_permissions()
        for path in os.listdir(dir_path):
            # check if current path is a file
            # if not os.path.isfile(os.path.join(dir_path, path)):
            #     pass
            pass

    # def give_permissions(self, user):
    #