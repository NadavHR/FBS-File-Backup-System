import datetime
import json
import os
import shutil

import constants


class Project(constants.Constants):

    def __init__(self, user_name: str, project_name: str, project_description: str = "",
                 creation_time: datetime.datetime = datetime.datetime.now()):
        self.user_name = user_name
        self.project_name = project_name
        self.project_description = project_description
        self.creation_time = creation_time

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
        if os.path.exists(dir_path):
            for path in os.listdir(dir_path):
                # check if current path is a file
                if not os.path.isfile(os.path.join(dir_path, path)):
                    perms.append(
                        (path, os.path.isfile(os.path.join(dir_path, f"{path}\\{Project.WRITE_PERMISSION_FILE_NAME}"))))
        else:  # permissions path doesnt exist
            os.mkdir(dir_path)

        return perms

    def give_permissions(self, user, write):
        """
        gives permissions to a user DOES NOT MAKE SURE PROJECT PERMISSIONS DON'T GO ABOVE SHARING LIMIT, OR THAT THE
        USER BEING GIVEN PERMISSIONS ISN'T THE OWNER
        :param user: the name of the user to give permissions to
        :param write: True for write access, False for readonly
        """
        path_to_user_perms = f"{self.path_to_permissions()}\\{user}"
        if write:
            f = open(f"{path_to_user_perms}\\{Project.WRITE_PERMISSION_FILE_NAME}", "wb+")
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

    def path_to_n_commit(self, n: int) -> str:
        """
        gives you the path to the n'th commit
        :param n: the number of the commit you want to get
        :return: the path to the n'th commit in the project
        """
        if (n >= self.count_commits()) or (n < 0):
            raise Exception("can not access a negative or non existent commit")
        last = f"\\{Project.COMMIT_DIR}"
        return f"{self.path_to_latest_commit()}{ last * (self.count_commits() - n - 1)}"

    def commit(self, data: bytes) -> bool:
        """
        commits the data as a new commit, DOES NOT MAKE SURE DATA DOES NOT EXCEED SIZE LIMIT
        DON'T USE THIS FUNCTION DIRECTLY, use the ProjectManager or maybe in specific cases the Commit class
        :param data: the data we want to commit as bytes
        :return: True if successfully added a new commit and False if the project does not exist or exceeds commit limit
        """
        if not self.exists():
            return False

        latest = self.path_to_latest_commit()
        num_file_path = f"{latest}\\{Project.COMMIT_NUMBER_FILE}"
        data_file_path = f"{latest}\\{Project.COMMIT_DATA_FILE}"
        metadata_file_path = f"{latest}\\{Project.COMMIT_METADATA_FILE}"
        num = self.count_commits()
        if num == 0:  # case of first commit
            os.mkdir(latest)
            f = open(num_file_path, "wb+")
            f.write(b"\x00")
            f.close()
            f = open(data_file_path, "wb+")
            f.write(data)
            f.close()
        elif num == Project.COMMIT_LIMIT:  # project exceeds commit limit
            return False
        else:
            temp_folder = f"{latest}\\temp"
            os.mkdir(temp_folder)
            shutil.move(num_file_path, temp_folder)
            shutil.move(data_file_path, temp_folder)
            shutil.move(metadata_file_path, temp_folder)
            if num > 1:  # only move the path to the next commit if it exists
                shutil.move(f"{latest}\\{Project.COMMIT_DIR}", temp_folder)
            os.rename(temp_folder, f"{latest}\\{Project.COMMIT_DIR}")

            f = open(num_file_path, "wb+")
            f.write(num.to_bytes(1, "big"))
            f.close()
            f = open(data_file_path, "wb+")
            f.write(data)
            f.close()

        return True

    def delete_commit(self, commit_number: int) -> bool:
        """
        deletes a commit if it exists ONLY USE AFTER MAKING SURE THE USER REQUESTING DELETION IS AUTHORIZED TO DO SO
        :param commit_number: the number of the commit we want to delete
        :return: true if the commit was successfully deleted false if it didn't exist
        """

        # TODO: finish this

    def count_commits(self) -> int:
        """
        checks how many commits the project has
        :return: the amount of commits the project has
        """
        latest = self.path_to_latest_commit()
        num_file_path = f"{latest}\\{Project.COMMIT_NUMBER_FILE}"
        if os.path.isfile(num_file_path):
            f = open(num_file_path, "rb")
            num = int.from_bytes(f.read(), "big")
            f.close()
            return num + 1
        else:
            return 0

    def delete(self) -> bool:
        """
        deletes this project, ONLY USE IF THE DELETING USER HAS PERMISSIONS TO DELETE
        :return: True if the project was deleted False if it didnt exist
        """
        if self.exists():
            shutil.rmtree(self.to_path())
            return True
        else:
            return False

    def create(self) -> bool:
        """
        attempts to create the project if it doesnt already exist or fails the size limits,
        DOES NOT MAKE SURE THE PROJECT IS LEGAL IN ANY WAY OTHER THAN SIZE LIMITS, DO NOT USE THIS FUNCTION DIRECTLY,
        USE ProjectManager
        :return: true if successfully created the project, else false
        """
        if self.exists():  # project already exists
            return False
        if len(self.project_description) > Project.PROJECT_DESCRIPTION_SIZE_LIMIT:  # project description too long
            return False
        if len(self.project_name) > Project.PROJECT_NAME_SIZE_LIMIT:  # project name too long
            return False

        path_to_project = self.to_path()
        os.mkdir(path_to_project)
        self.creation_time = datetime.datetime.now()
        f = open(f"{path_to_project}\\{Project.PROJECT_METADATA_FILE}", "w+")
        f.write(json.dumps({Project.PROJECT_DESCRIPTION_FIELD: self.project_description,
                            Project.PROJECT_DATE_FIELD: self.creation_time}, default=str))
        f.close()

        return True

    def __eq__(self, other):
        return (self.project_name == other.project_name) and (self.user_name == other.user_name)
