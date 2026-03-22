class LoggerError(Exception):
    """Raised when an error occoures in the Logger configuration"""
    def __init__(self, message):
        super().__init__(message)

class InvalidIpInvalidIpError(Exception):
    """Raised when the client Ip is invalid"""