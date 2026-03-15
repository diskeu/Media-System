class EmailAlreadyExistsError(BaseException):
    def __init__(self, message = None):
        if not message: message = "Email Already Exists"
        super().__init__(message)

class UserNameAlreadyExistsError(BaseException):
    def __init__(self, message = None):
        if not message: message = "User Already Exists"
        super().__init__(message)