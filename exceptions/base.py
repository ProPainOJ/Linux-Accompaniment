from abc import ABC, abstractmethod


class MyBaseException(Exception, ABC):
    @abstractmethod
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return str(self.message)
