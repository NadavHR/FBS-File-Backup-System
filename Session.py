import time
import constants

existing_sessions = set()


class Session(constants.Constants):
    def __init__(self):
        self.id = Session._generate_id()
        self.time = time.time()

    @staticmethod
    def _generate_id() -> int:
        return sum(existing_sessions) + 1

    def refresh(self):
        self.time = time.time()

    def expire(self):
        """
        expires a session
        """
        existing_sessions.remove(self.id)
