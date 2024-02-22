class Response:
    RESPONSE_SUCCESS_FIELD = "success"
    RESPONSE_MESSAGE_FIELD = "message"

    def __init__(self, success=False, response_message="Change Me"):
        self._success = success
        self._response_message = response_message

    @property
    def success(self):
        return self._success

    @property
    def response_message(self):
        return self._response_message

    def to_dict(self):
        return {self.RESPONSE_SUCCESS_FIELD: self._success,
                self.RESPONSE_MESSAGE_FIELD: self.response_message}

    def __eq__(self, other):
        return (not (self._success ^ other.success)) and (self._response_message == other.response_message)

    def __str__(self):
        return f"success: {self._success}  response: {self._response_message}"
