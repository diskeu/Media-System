class NotNullError():
    """Raised when Null gets parsed into a Not Null field"""
    def __init__(self, message = None):
        if message == None: message = "Field cannot be Null"
        super().__init__(message)