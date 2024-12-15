from abc import ABC, abstractmethod
from typing import TypedDict, NotRequired

from bson import ObjectId

from exceptions.app import ValidationException
from property.helpers import cust_join

type KeyTypes = int | float | str
type MongoTypes = ObjectId | KeyTypes | list | dict


class BaseNotificationDTO(TypedDict):
    extra_args: NotRequired[dict[KeyTypes, MongoTypes]]


class SetNotificationDTO(BaseNotificationDTO):
    action: list[str]
    title: str
    description: NotRequired[str]


class GetNotificationDTO(BaseNotificationDTO, total=False):
    _id: ObjectId


class NotificationDTO(GetNotificationDTO, SetNotificationDTO, total=False): pass


class BaseNotification(ABC):
    AVAILABLE_ACTION = frozenset({"open_url", "remind", "show"})
    EXTRA_ARGS: str = "extra_args"

    def __call__(self) -> SetNotificationDTO:
        return self.__dict__()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{id(self)}>: " + str(self.__dict__())

    def __repr__(self) -> str:
        return self.__str__()

    def __dict__(self) -> SetNotificationDTO:
        return self.notify

    def __iter__(self) -> tuple[KeyTypes, MongoTypes]:
        for key, value in self.notify.items():
            yield key, value

    def __getitem__(self, item: KeyTypes) -> MongoTypes:
        return self.notify[item]

    def to_dict(self) -> dict[str, MongoTypes]:
        return self.__dict__()

    def _realize_extra_args(self) -> None:
        """Распаковка `extra_args` в основной словарь."""
        if self.notify.get(self.EXTRA_ARGS):
            if self.notify[self.EXTRA_ARGS]:
                self.notify = self.notify | self.notify[self.EXTRA_ARGS]
            del self.notify[self.EXTRA_ARGS]

    @abstractmethod
    def __init__(self, notify: SetNotificationDTO | GetNotificationDTO) -> None:
        self.notify = notify
        self._validate()
        self._realize_extra_args()

    @abstractmethod
    def _validate(self, *args, **kwargs) -> ValidationException | None:
        pass


class CreateNotification(BaseNotification):
    """Создание DTO-объекта Notification."""

    def __init__(self, notify: SetNotificationDTO) -> None:
        super().__init__(notify)

    def __getitem__(self, item: KeyTypes) -> MongoTypes:
        if item not in self.notify:
            raise ValueError(f"Недопустимый ключ - <{item}>! Доступные ключи [{cust_join(tuple(self.notify.keys()))}]")
        return self.notify[item]

    def _validate(self) -> ValidationException | None:
        validated_field, bad_params = "action", ()
        if len(self.notify["title"]) == 0:
            raise ValidationException("Длинна аргумента `title` должны быть более 0!")
        if isinstance(self.notify[validated_field], str) and self.notify[validated_field] in self.AVAILABLE_ACTION:
            self.notify[validated_field] = [self.notify[validated_field]]
        else:
            for param in self.notify[validated_field]:
                if param not in self.AVAILABLE_ACTION:
                    bad_params += (param,)
        if bad_params:
            raise ValidationException(
                msg=f"Недопустимые аргументы `action` - [{cust_join(bad_params)}]!"
                    f" Доступные параметры [{cust_join(tuple(self.AVAILABLE_ACTION))}]"
            )
        return


class GetNotification(BaseNotification):

    def __init__(self, notify_dict: dict[KeyTypes, MongoTypes]) -> None:
        self.notify = NotificationDTO()  # type: ignore
        extra_args = {}
        for key, value in notify_dict.items():  # type: KeyTypes, MongoTypes
            if key not in NotificationDTO.__annotations__.keys() and key != self.EXTRA_ARGS:
                extra_args |= {key: value}
            else:
                self.notify |= {key: value}
        else:
            self.notify |= {self.EXTRA_ARGS: extra_args}

    def _validate(self) -> ValidationException | None:
        pass
