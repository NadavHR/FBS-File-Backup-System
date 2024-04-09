import call_endpoints

class User:

    def __init__(self, name, password):
        self.name = name
        self.password = password


    def login(self) -> (bool, str):
        resp, message = call_endpoints.login(self.name, self.password)
        return resp, message



