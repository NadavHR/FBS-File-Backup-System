import os
import shutil

import project_manager
from session import Session
import constants

users_to_sessions = {}  # key user_name:str  value session:Session


class User(constants.Constants):
    def __init__(self, user_name: str, password_hash: bytes, session: Session = None):
        self.user_name = user_name
        self.password_hash = password_hash
        self.session = session
        if not (session is None):
            if user_name in users_to_sessions:
                users_to_sessions[user_name].expire()
            users_to_sessions[user_name] = session
        elif user_name in users_to_sessions:
            self.session = users_to_sessions[user_name]

    def exists(self) -> bool:
        """
        checks if the user exists
        :return: True if the user exists, false otherwise
        """
        return project_manager.ProjectManager.is_user(self.user_name)

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
        if self.session is None:
            self.session = Session(self.user_name)
            users_to_sessions[self.user_name] = self.session
        return True

    def delete(self) -> bool:
        """
        deletes an existing user
        :return: True if successfully deleted, else false
        """
        if not self.exists():
            return False

        shutil.rmtree(self.to_path())
        self.session.expire()

    def auth_login(self) -> bool:
        """
        authenticates the user (checks if the user's password matches the one stored)
        :return: True if the user's login is legal, else false
        """
        if not self.exists():
            return False
        self.session.refresh()
        return self.password_hash == self._get_password_hash()

    def auth_user(self) -> bool:
        """
        authenticates the user to check if its allowed to perform an action (auths both password and session)
        :return: True if the user is authenticated else false
        """
        return self.auth_login() and (self.session.get_session_user() == self.user_name) and (self.session.auth())

    @classmethod
    def _from_name(cls, user_name: str):
        """
        generates a user from his user name, UNSAFE as it doesnt authenticate anything like the session
        :return: the user
        """
        user = cls(user_name, b"")
        f = open(user.path_to_password(), "rb")
        user.password_hash = f.read()
        f.close()
        return user

    @classmethod
    def from_session(cls, session: Session):
        """
        generates a user from his Session
        :param session: the session
        :return: the user who started the session if the session is valid, else returns None
        """
        if session.auth():
            return cls._from_name(session.get_session_user())
        return None

    @classmethod
    def from_session_id(cls, session_id: int):
        """
        generates a user from his session
        :param session_id: the id of the session
        :return: the user who started the session if the session is valid, else returns None
        """
        session = Session.from_session_id(session_id)
        return cls.from_session(session)
