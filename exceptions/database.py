from exceptions.base import MyBaseException


class DataBaseBaseException(MyBaseException):
    NAME_EXCEPTION = "ERROR Application >>>\t"

    def __init__(self, message: str) -> None:
        super().__init__(self.NAME_EXCEPTION + message)


class ConfigException(DataBaseBaseException): pass
