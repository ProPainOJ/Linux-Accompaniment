from enum import Enum


class Singleton:
    """Паттерн сингелтон для настроек, логгера и т.д."""
    _instances = {}

    def __new__(cls, *args, **kwargs):
        cls.FIRST_START: bool = False
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            cls.FIRST_START = True
        return cls._instances[cls]


class BaseEnum(str, Enum):
    """Упрощённый ENUM, чтобы сразу вызывать ``.value``."""

    def __str__(self) -> str:
        return str.__str__(self)
