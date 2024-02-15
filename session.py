import time
import constants

ids_to_sessions = {}  # key id:int  value: Session


class Session(constants.Constants):
    def __init__(self, user: str):
        """
        creates a new session
        :param user: the name of the user that started the session
        """
        self.id = Session._generate_id()
        ids_to_sessions[self.id] = self
        self.start_time = time.time()
        self._user = user

    @staticmethod
    def _generate_id() -> int:
        """
        generates a new unused session id
        :return: the int of the session id
        """
        return sum(ids_to_sessions.keys()) + 1

    @staticmethod
    def from_session_id(session_id: int):
        """
        returns a session based on its id
        :param session_id: the id of the session
        :return: a Session object representing the session with the given id or throws an exception if the id doesnt
         exist
        """
        if not Session.is_session(session_id):
            raise Exception("session does not exist")
        return ids_to_sessions[session_id]

    @staticmethod
    def is_session(session_id: int) -> bool:
        """
        checks if a session exists
        :param session_id: the id of the session to check
        :return: True if the session exists else false
        """
        return session_id in ids_to_sessions

    def refresh(self):
        """
        refreshes a session pushing back its expiration time
        """
        self.start_time = time.time()

    def expire(self):
        """
        expires a session
        """
        ids_to_sessions.pop(self.id)

    def auth(self) -> bool:
        """
        checks if a session is valid, DOES NOT EXPIRE INVALID SESSIONS BY ITSELF
        :return: True if the session is valid, false otherwise
        """
        return ((self.start_time + Session.SESSION_LIFETIME_SECONDS) > time.time()) and (self.is_session(self.id))

    def get_session_user(self) -> str:
        """
        returns the name of the user who started the session
        :return: a string representing the name of the user who started the session
        """
        return self._user
