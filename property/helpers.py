from datetime import datetime, timedelta
from typing import Any, Sequence

from typing_extensions import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def cust_join(iter_object: Sequence[str], separation: str = ", ") -> str | None:
    if not iter_object: return
    if len(iter_object) == 1:
        return str(iter_object[0])
    return f"{separation}".join(iter_object)


def is_iterable(obj: Any) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def get_sec_to_target(start_data: datetime = datetime.now(), delta_data: timedelta = timedelta(days=1)) -> timedelta:
    """
    Получение секунд к указанной ``start_data`` + ``delta_data``.

    :param start_data: Время от которого считать.
    :param delta_data: Сколько добавить к ``start_data``

    :return: Сколько секунд осталось до цели.
    """

    next_data = start_data + delta_data
    delta_data = next_data - datetime.now()

    return delta_data


def get_key_dict_by_value(_dict: dict[K, V], _dict_value: V, first_key: bool = True) -> K | tuple[K, ...] | None:
    """
    Получение ключа(ей) словаря по его значению.

    :param _dict: Словарь для поиска ключей.
    :param _dict_value: Значение для поиска ключей.
    :param first_key: Искать только первое совпадение.

    :return: Ключи словаря соответствующие значению ``_dict_value``.
    """
    if not first_key:
        return tuple((key for key, value in _dict.items() if value == _dict_value)) or None
    return next((key for key, value in _dict.items() if value == _dict_value), None)
