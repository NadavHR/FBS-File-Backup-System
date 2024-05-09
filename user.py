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
        if not (os.path.exists(User.USERS_DIR)):
            os.makedirs(User.USERS_DIR)
        if not (session is None):
            if session.get_session_user() == user_name:
                if user_name in users_to_sessions:
                    users_to_sessions[user_name].expire()
                users_to_sessions[user_name] = session
                self._session = session
        elif user_name in users_to_sessions:
            self._session = users_to_sessions[user_name]
        else:
            self._session = None

    def generate_session(self) -> bool:
        """
        generates a new session for this user (if legal)
        :return: True if successfully generated new session else false
        """
        if self.auth_user_session():
            return False  # user already has session

        if self.user_name in users_to_sessions:
            if users_to_sessions[self.user_name].auth() and users_to_sessions[self.user_name].user == self.user_name:
                return False  # user already has session

        if not self.auth_login():
            return False

        self._session = Session(user=self.user_name)
        users_to_sessions[self.user_name] = self._session
        return True

    def end_session(self) -> bool:
        """
        end an existing session (if legal)
        :return: True if session successfully ended, else false
        """
        if not self.auth_user_session():
            return False  # session already invalid
        users_to_sessions.pop(self.user_name)
        self.session.expire()
        return True

    @property
    def session(self) -> Session:
        return self._session

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
            self._session = Session(self.user_name)
            users_to_sessions[self.user_name] = self.session
        return True

    def delete(self) -> bool:
        """
        deletes an existing user
        :return: True if successfully deleted, else false
        """
        if not self.exists():
            return False
        self.end_session()
        shutil.rmtree(self.to_path())
        if not (self.session is None):
            self.session.expire()
        return True

    def auth_login(self) -> bool:
        """
        authenticates the user (checks if the user's password matches the one stored)
        :return: True if the user's login is legal, else false
        """
        if not self.exists():
            return False
        return self.password_hash == self._get_password_hash()

    def auth_user_session(self) -> bool:
        """
        authenticates the user to check if its allowed to perform an action (auths session)
        NOT the same as calling user.session.auth as it makes sure the session belongs to this user
        :return: True if the user is authenticated else false
        """
        if self.session is None:
            return False
        return (self.session.get_session_user() == self.user_name) and (self.session.auth()) and self.exists()

    @classmethod
    def _from_name(cls, user_name: str):
        """
        generates a user from his user name, UNSAFE as it doesnt authenticate anything like the session
        :return: the user
        """
        user = cls(user_name, b"")
        if user.exists():
            f = open(user.path_to_password(), "rb")
            user.password_hash = f.read()
            f.close()
            return user
        return None

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
        if Session.is_session(session_id):
            session = Session.from_session_id(session_id)
            return cls.from_session(session)
        return None
