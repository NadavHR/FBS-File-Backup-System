import datetime
import json
import os
import shutil

from ProjectClass import Project
import constants


class Commit(constants.Constants):

    def __init__(self, commit_number: int, user: str, date: datetime.datetime, commit_name: str, commit_message: str,
                 data: bytes, project: Project):
        self.commit_number = commit_number
        self.user = user
        self.commit_time = date
        self.commit_name = commit_name
        self.commit_message = commit_message
        self.data = data
        self.project = project

    @classmethod
    def new_commit(cls, user: str, commit_name: str, commit_message: str, data: bytes, project: Project):
        """
        constructs a new commit that exists at the top of the project DOES NOT MAKE SURE ITS LEGAL OR AND DOES
        NOT COMMIT IT
        :param user: the user who requested the commit
        :param commit_name: name of commit
        :param commit_message: commit message
        :param data: the data (bytes)
        :param project: the project the commit belongs to
        :return: a new Commit object that (if committed) exists at the top of the project
        """
        return cls(commit_number=project.count_commits(), date=datetime.datetime.now(), user=user,
                   commit_name=commit_name, commit_message=commit_message, data=data, project=project)

    @classmethod
    def from_commit_number(cls, commit_number: int, project: Project):
        """
        constructs a new object that represents a specific commit
        :param commit_number: the number of the commit
        :param project: the project the commit belongs to
        :return: a new Commit object that represents an existing commit
        """
        path_to_commit = project.path_to_n_commit(commit_number)
        f = open(f"{path_to_commit}\\{Commit.COMMIT_METADATA_FILE}", "r")
        metadata = json.loads(f.read())
        f.close()
        f = open(f"{path_to_commit}\\{Commit.COMMIT_DATA_FILE}", "rb")
        data = f.read()
        f.close()
        return cls(commit_number=commit_number, project=project, commit_name=metadata[Commit.COMMIT_NAME_FIELD],
                   data=data, commit_message=metadata[Commit.COMMIT_MSG_FIELD], user=metadata[Commit.COMMIT_USER_FIELD],
                   date=datetime.datetime.strptime(metadata[Commit.COMMIT_DATE_FIELD], "%Y-%m-%d %H:%M:%S.%f"))

    def to_metadata(self) -> str:
        """
        makes the metadata file's content's DOESNT MAKE SURE THE COMMIT IS LEGAL
        :return: the string (written as a json) of the commits metadata
        """
        return json.dumps({Commit.COMMIT_NAME_FIELD: self.commit_name,
                           Commit.COMMIT_DATE_FIELD: self.commit_time,
                           Commit.COMMIT_USER_FIELD: self.user,
                           Commit.COMMIT_MSG_FIELD: self.commit_message,
                           }, default=str)

    def is_legal(self) -> bool:
        """
        checks if the commit is legal, DOES NOT CHECK IF THE USER IS VALID OR IF THE TIME MAKES SENSE
        :return: true if the commit is legal, false if illegal for any reason
        """
        return (self.commit_number >= 0) and \
               (self. commit_number < Commit.COMMIT_LIMIT) and \
               (len(self.commit_name) <= Commit.COMMIT_NAME_LIMIT) and \
               (len(self.commit_message) <= Commit.COMMIT_MESSAGE_LIMIT) and \
               (len(self.data) <= Commit.COMMIT_SIZE_LIMIT)

    def commit(self) -> bool:
        """
        attempts to commit this commit to the top of the project
        :return: true if successfully committed, false if commit failed for any reason
        """
        if not self.is_legal():  # illegal commit
            return False

        if self.project.count_commits() > self.commit_number:  # cant commit back in time
            return False
        # no real point in checking if the commit is forward in time as we can just take it back
        # we honestly don't care enough to make sure the date is after the last date, it really doesnt matter

        if not self.project.commit(self.data):  # if the project failed to commit
            return False

        path_to_metadata = f"{self.project.path_to_latest_commit()}\\{Commit.COMMIT_METADATA_FILE}"
        f = open(path_to_metadata, "w+")
        f.write(self.to_metadata())
        f.close()

        return True

    def exists(self) -> bool:
        """
        checks if a commit exists
        :return: true if the commit exists, false otherwise
        """
        try:
            c = Commit.from_commit_number(self.commit_number, self.project)
            return self == c
        except:
            return False

    def delete(self) -> bool:
        """
        attempts to delete the commit
        :return: true if the commit was deleted, false otherwise
        """
        if not self.exists():  # commit doesnt exist
            return False

        def decrease_all_by_1(index: int):
            """decreases all of the commits after n (including) by 1"""
            for i in range(self.project.count_commits() - index):
                num_file_path = f"{self.project.path_to_n_commit(index + i)}\\{Commit.COMMIT_NUMBER_FILE}"
                f = open(num_file_path, "rb")
                num = int.from_bytes(f.read(), "big")
                f.close()
                f = open(num_file_path, "wb+")
                f.write((num - 1).to_bytes(1, "big"))
                f.close()

        path_to_commit = self.project.path_to_n_commit(self.commit_number)
        if self.commit_number == (self.project.count_commits() - 1):  # case of latest commit
            pass
        else:
            n = self.commit_number + 1
            path_to_parent_commit = self.project.path_to_n_commit(n)
            if n > 0:  # case of not first commit
                path_to_prev_commit = self.project.path_to_n_commit(self.commit_number - 1)
                temp_folder = f"{path_to_parent_commit}\\temp"
                os.mkdir(temp_folder)
                for path in os.listdir(path_to_prev_commit):
                    shutil.move(f"{path_to_prev_commit}\\{path}", temp_folder)
                shutil.rmtree(path_to_commit)
                os.rename(temp_folder, path_to_commit)
                decrease_all_by_1(n)

            else:
                pass
        return True
        # TODO: finish this


    def __eq__(self, other):
        return (self.project == other.project) and \
               (self.commit_number == other.commit_number) and \
               (self.commit_name == other.commit_name) and \
               (self.commit_message == other.commit_message) and \
               (self.user == other.user) and \
               (self.data == other.data) and \
               (self.commit_time == other.commit_time)
