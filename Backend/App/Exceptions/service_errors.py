class NotNullError():
    """Raised when Null gets parsed into a Not Null field"""
    def __init__(self, message = "Field cannot be Null"):
        super().__init__(message)