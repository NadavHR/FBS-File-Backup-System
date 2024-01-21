
class Response:
    def __init__(self, success=False, response_message="Change Me"):
        self.success = success
        self.response_message = response_message

    def __eq__(self, other):
        return (not (self.success ^ other.success)) and (self.response_message == other.response_message)
