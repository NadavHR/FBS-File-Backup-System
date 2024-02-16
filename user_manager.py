import datetime

import constants
from response import Response
from user import User
from project_manager import ProjectManager
from project_class import Project
from commit import Commit

class UserManager(constants.Constants):

    @staticmethod
    def _check_user_session(user: User = None) -> bool:
        """
        checks if a user is in a legal session, if the user is None they have an illegal session
        :param user: the user we want to check
        :return: True for a legal session, else false
        """
        if user is None:
            return False
        if user.auth_user_session():
            return True
        return False

    @staticmethod
    def create_user(user_name: str, password_hash: bytes) -> Response:
        """
        creates a new user if possible
        :param user_name: the name of the user we want to create
        :param password_hash: the hash of the password of the user
        :return:
        """
        user = User(user_name, password_hash)
        if user.exists():
            return UserManager.E_USER_ALREADY_EXISTS
        if not user.create():
            return UserManager.E_UNKNOWN_ERROR
        return Response(success=True, response_message=f"{user.session.id}")

    @staticmethod
    def delete_user(session_id: int) -> Response:
        """
        deletes a user if the request is legal
        :param session_id: the id of the session
        :return: a response object
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        if not user.delete():
            return UserManager.E_UNKNOWN_ERROR
        return UserManager.S_USER_DELETED

    @staticmethod
    def login(user_name: str, password_hash: bytes) -> Response:
        """
        takes in a user name and password and if legal generates a new session for this user
        :param user_name: the name of the user to login
        :param password_hash: the hash of the password of the user
        :return: a response detailing whether the action was successful or not
        """
        user = User(user_name, password_hash)
        if not user.auth_login():
            return UserManager.E_BAD_LOGIN_CREDENTIALS
        if user.auth_user_session():
            return UserManager.E_USER_ALREADY_HAS_VALID_SESSION
        if not user.generate_session():
            return UserManager.E_UNKNOWN_ERROR
        return Response(success=True, response_message=f"{user.session.id}")

    @staticmethod
    def logout(session_id: int) -> Response:
        """
        logs a user out
        :param session_id: the id of the session
        :return: a Response detailing the actions response
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        if not user.end_session():
            return UserManager.E_UNKNOWN_ERROR
        return UserManager.S_LOGGED_OUT

    @staticmethod
    def commit(session_id: int, commit: Commit) -> Response:
        """
        commits a commit to a project
        :param session_id: the id of the session
        :param commit: the commit we want to make
        :return: Response detailing the actions success
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        if commit.user != user.user_name:
            return UserManager.E_UNKNOWN_ERROR
        user.session.refresh()
        return ProjectManager.commit_to(project=commit.project, commit=commit)

    @staticmethod
    def delete_commit(session_id: int, commit: Commit) -> Response:
        """
        deletes a commit from a project
        :param session_id: the id of the session
        :param commit: the commit we want to delete
        :return: Response detailing the actions success
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        user.session.refresh()
        if not (commit.project.user_name == user.user_name):
            return UserManager.E_BAD_PERMISSIONS
        return ProjectManager.delete_commit(commit=commit)

    @staticmethod
    def add_project(session_id: int, project_name: str, project_description: str) -> Response:
        """
        creates a new project
        :param session_id: the id of the session
        :param project_name: the name of the project you want to create
        :param project_description: a description of the project
        :return: response object detailing the actions success
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        project = Project(user_name=user.user_name, project_name=project_name, project_description=project_description,
                          creation_time=datetime.datetime.now())
        user.session.refresh()
        return ProjectManager.add_project(project)

    @staticmethod
    def delete_project(session_id: int, project_name: str) -> Response:
        """
        deletes a project
        :param session_id: the id of the session
        :param project_name: the name of project to delete
        :return: a response detailing the actions success
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        project = Project(user_name=user.user_name, project_name=project_name)
        return ProjectManager.delete_project(project)

    @staticmethod
    def update_project_permissions(session_id: int, project_name: str, user_name: str, write: bool = None) -> Response:
        """
        updates a project's permissions
        :param session_id: the id of the current session
        :param project_name: the name of the project we want to update permissions to
        :param user_name: the name of the user we want to update permissions to
        :param write: which access to give the user, True for write, False for readonly and None for none
        :return: a response detailing the actions success
        """
        user = User.from_session_id(session_id)
        if not UserManager._check_user_session(user):
            return UserManager.E_BAD_SESSION
        project = Project(project_name=project_name, user_name=user.user_name)
        return ProjectManager.update_project_permissions(user_name, project, write)

