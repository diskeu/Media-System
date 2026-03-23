class EmailAlreadyExistsError(BaseException):
    def __init__(self, message = "Email Already Exists"):
        super().__init__(message)

class UserNameAlreadyExistsError(BaseException):
    def __init__(self, message = "User Already Exists"):
        super().__init__(message)

class InvalidPasswordError(BaseException):
    def __init__(self, message = "Password should Contain 8 - 20 char, atleast one upper & lower case letter, one number and one special char. Allowed char: A-Za-z, @$#%*!?"):
        super().__init__(message)

class InvalidEmailError(BaseException):
    def __init__(self, message = "Email is invalid"):
        super().__init__(message)