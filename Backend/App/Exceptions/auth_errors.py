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

class InvalidUserError(BaseException):
    def __init__(self, message = "User doesn't exist"):
        super().__init__(message)


class InvalidEmailVerficationTokenError(BaseException):
    def __init__(self, message = "Registration Token is invalid or expired"):
        super().__init__(message)

class InvalidRefreshTokenError(BaseException):
    def __init__(self, message = "Given RefreshToken is invalid"):
        super().__init__(message)

class ExpiredRefreshTokenError(InvalidRefreshTokenError):
    def __init__(self, message = "Given RefreshToken has expired"):
        super().__init__(message)

class ReplacedRefreshTokenUseError(InvalidRefreshTokenError):
    def __init__(self, message = "Given RefreshToken has already been replaced"):
        super().__init__(message)