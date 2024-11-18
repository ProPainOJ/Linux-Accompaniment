from exceptions.base import MyBaseException


class ApplicationException(MyBaseException):
    NAME_EXCEPTION = "ERROR Application >>>\t"

    def __init__(self, msg):
        super().__init__(self.NAME_EXCEPTION + msg)


class ValidationException(ApplicationException): pass