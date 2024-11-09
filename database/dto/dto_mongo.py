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
    name: str
    action: list[str]
    title: str
    description: NotRequired[str]


class GetNotificationDTO(BaseNotificationDTO, total=False):
    _id: ObjectId


class NotificationDTO(GetNotificationDTO, SetNotificationDTO, total=False): pass


class BaseNotification(ABC):
    AVAILABLE_ACTION = frozenset({"open_url", "remind", "show"})

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

    def to_dict(self) -> dict[str, MongoTypes]:
        return self.__dict__()

    def _realize_extra_args(self) -> None:
        """Распаковка `extra_args` в основной словарь."""
        args_key = "extra_args"
        if self.notify.get(args_key):
            if self.notify[args_key]:
                self.notify = self.notify | self.notify[args_key]
            del self.notify[args_key]

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
            raise ValueError(f"Недопустимый ключ - <{item}>! Доступные ключи [{cust_join(self.notify.keys())}]")
        return self.notify[item]

    def _validate(self) -> ValidationException | None:
        validated_field, bad_params = "action", ()
        if len(self.notify["name"]) == 0 or len(self.notify["title"]) == 0:
            raise ValidationException("Длинна аргументов `name` и `title` должны быть более 0!")
        for param in self.notify[validated_field]:
            if param not in self.AVAILABLE_ACTION:
                bad_params += (param,)
        if bad_params:
            raise ValidationException(
                msg=f"Недопустимые аргументы `action` - [{cust_join(bad_params)}]!"
                    f" Доступные параметры [{cust_join(self.AVAILABLE_ACTION)}]"
            )
        return


class GetNotification(BaseNotification):

    def __init__(self, notify: GetNotificationDTO) -> None:
        super().__init__(notify)

    def _validate(self) -> ValidationException | None:
        pass
