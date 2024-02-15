import constants
from response import Response
from user import User
from session import Session

class UserManager(constants.Constants):

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
    def delete_user(user_name: str, session: Session) -> Response:
        """
        deletes a user if the request is legal
        :param user_name:
        :param session:
        :return:
        """
