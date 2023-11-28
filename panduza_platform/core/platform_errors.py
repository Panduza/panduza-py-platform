

class InitializationError(Exception):
    """Exception raised when an initialization fails, causing the platform stop
    """
    def __init__(self, message):
        super().__init__(message)

