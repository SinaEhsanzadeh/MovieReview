class NotFoundError(Exception):
    def __init__(self, message: str = "Not Found"):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    def __init__(self, message: str = "Validation Error"):
        self.message = message
        super().__init__(message)