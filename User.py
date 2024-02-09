import os
import shutil

import ProjectManager
import Session
import constants


class User(constants.Constants):
    def __init__(self, user_name: str, password_hash: bytes, session: Session.Session = None):
        self.user_name = user_name
        self.password_hash = password_hash
        self.session = session

    def exists(self) -> bool:
        """
        checks if the user exists
        :return: True if the user exists, false otherwise
        """
        return ProjectManager.ProjectManager.is_user(self.user_name)

    def to_path(self):
        return f"{User.USERS_DIR}\\{self.user_name}"

    def path_to_password(self):
        return f"{self.to_path()}\\{User.USER_PASSWORD_FILE}"

    def path_to_projects(self):
        return f"{self.to_path()}\\{User.USER_PROJECTS_DIR}"

    def path_to_shared(self):
        return f"{self.to_path()}\\{User.USER_SHARED_DIR}"

    def _get_password_hash(self) -> bytes:
        """
        gets the passwords hash, DOES NOT MAKE SURE THE USER EXISTS
        :return: returns the hash of the password as stored
        """
        f = open(self.path_to_password(), "rb")
        p = f.read()
        f.close()
        return p

    def create(self) -> bool:
        """
        creates a new user
        :return: True if the user can be created, false otherwise
        """
        if self.exists():
            return False
        path_to_user = self.to_path()
        os.mkdir(path_to_user)
        os.mkdir(self.path_to_shared())
        os.mkdir(self.path_to_projects())
        f = open(self.path_to_password(), "wb+")
        f.write(self.password_hash)
        f.close()
        self.session = Session.Session()

    def delete(self) -> bool:
        """
        deletes an existing user
        :return: True if successfully deleted, else false
        """
        if not self.exists():
            return False

        shutil.rmtree(self.to_path())
        self.session.expire()

    def auth_login(self):
        """
        authenticates the user (checks if the user's password matches the one stored)
        :return: True if the user's login is legal, else false
        """
        if not self.exists():
            return False
        self.session.refresh()
        return self.password_hash == self._get_password_hash()

