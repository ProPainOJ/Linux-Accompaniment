from exceptions.base import MyBaseException
from property.constants import EXCEPTIONS


class ZenityBaseException(MyBaseException):
    NAME_EXCEPTION = "Zenity >>> "

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(self.NAME_EXCEPTION + self.msg)


class ArgsException(ZenityBaseException):
    def __init__(self, args: tuple[str, ...], msg: str = "") -> None:
        if msg:
            msg += "\n"
        super().__init__(msg + EXCEPTIONS["zen_info"].format(", ".join(args)))


class AbortZenityInsert(ZenityBaseException):
    def __init__(self, msg: str = "") -> None:
        self.msg = msg
        super().__init__(self.NAME_EXCEPTION + self.msg)
