import os
import shutil


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
    COMMIT_DIR = "last_commit"  # every commit has a folder named as such so it points to the last commit
    # to access commits {path_to_project}\({COMMIT_DIR}\*n) with n being the number of commits you want to go back
    COMMIT_DATA = "data"
    # to access commit data {path_to_commit}\{COMMIT_DATA}
    COMMIT_NUMBER_FILE = "n"  # a file that only contains the commit number
    # to access commit number {path_to_commit}\{COMMIT_NUMBER_FILE}


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
        """
        lists all of the permissions to the project
        :return: a list of tuples containing the name of the user and whether he has write access (True if he has)
        """
        dir_path = self.path_to_permissions()
        perms = []
        for path in os.listdir(dir_path):
            # check if current path is a file
            if not os.path.isfile(os.path.join(dir_path, path)):
                perms.append((path, os.path.isfile(os.path.join(dir_path, f"{path}\\{Project.WRITE_PERMISSION_FILE_NAME}"))))

        return perms

    def give_permissions(self, user, write):
        """
        gives permissions to a user DOES NOT MAKE SURE PROJECT PERMISSIONS DON'T GO ABOVE SHARING LIMIT
        :param user: the name of the user to give permissions to
        :param write: True for write access, False for readonly
        """
        path_to_user_perms = f"{self.path_to_permissions()}\\{user}"
        if write:
            f = open(f"{path_to_user_perms}\\{Project.WRITE_PERMISSION_FILE_NAME}", "wb")
            f.close()
        else:
            if not os.path.isdir(path_to_user_perms):
                os.mkdir(path_to_user_perms)
            elif os.path.isfile(f"{path_to_user_perms}\\{Project.WRITE_PERMISSION_FILE_NAME}"):
                os.remove(f"{path_to_user_perms}\\{Project.WRITE_PERMISSION_FILE_NAME}")
            # if none of these conditions that means the permissions dont need changing

    def delete_permission(self, user):
        """
        this function deletes all permissions for a certain user, ONLY USE AFTER AUTHENTICATING THE REQUEST IS MADE BY A
        SOURCE QUALIFIED FOR THIS ACTION
        :param user: the user to remove the permissions from
        """
        path_to_user_perms = f"{self.path_to_permissions()}\\{user}"
        if os.path.isdir(path_to_user_perms):
            shutil.rmtree(path_to_user_perms)

    def path_to_latest_commit(self) -> str:
        """
        gives the path tpo latest commit, DOES NOT MAKE SURE THE PROJECT EXISTS
        :return: the path to the latest commit in the project
        """
        return f"{self.to_path()}\\{Project.COMMIT_DIR}"

    def commit(self, data: bytes) -> bool:
        """
        commits the data as a new commit, DOES NOT MAKE SURE USER DOES NOT EXCEED COMMITS LIMIT
        :param data: the data we want to commit as bytes
        :return: True if successfully added a new commit and False if the project does not exist
        """
        if not self.exists():
            return False
        # TODO: finish this




