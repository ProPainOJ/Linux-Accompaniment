from __future__ import annotations

import asyncio as io
from collections.abc import Callable
from functools import wraps
from typing import Any

from typing_extensions import TypeVar

from exceptions.app import ApplicationException
from exceptions.zenity import ArgsException
from notification.base import BaseNotify, ProcessResult
from property.constants import EXCEPTIONS, ZENITY
from property.helpers import cust_join

T = TypeVar("T", bound=tuple)

type FormsValue = str
type FormsValues = tuple[FormsValue, ...]
type FormsFields = dict[str, FormsValues]


class Zenity(BaseNotify):
    """Класс для реализации команд Zenity и простых уведомлений в терминале."""
    FORMS_FIELDS_NAME: dict[int, str] = {1: "combo", 2: "list"}
    _method_count_param = None
    ZENITY_CMD = "zenity"
    ZENITY_ARGS: dict[str, Callable] = {
        "text": lambda x: f"--text={x}",
        "title": lambda x: f"--title={x}",
        "ok_label": lambda x: f"--ok-label={x}",
        "extra_button": lambda x: [f"--extra-button={el}" for el in x],
        "cancel_label": lambda x: f"--cancel-label={x}",
        "width": lambda x: f"--width={x}",
        "height": lambda x: f"--height={x}",
        "timeout": lambda x: f"--timeout={x}",
        "icon": lambda x: f"--icon={x}",
        "entry": lambda entries: (f"--add-entry={entry.capitalize()}" for entry in entries) if entries else (),
        "req_entry": lambda req_entry: (
            f"--add-entry=* {entry.capitalize()}" for entry in req_entry
        ) if req_entry else ("",),
        "calender": lambda cal_name: f"--add-calendar={cal_name}",
    }

    def __init__(self, title: str = None, extra_button: tuple[str, ...] | list[str] | set[str] | None = None,
                 ok_label: str = "ОК", cancel_label: str = "Отмена", width: int = None, height: int = None,
                 timeout: int = None) -> None:
        """
        Создание основных параметров уведомления Zenity.

        :param title: Заголовок.
        :param ok_label: Кнопка "ОК".
        :param cancel_label: Кнопка "Отмена".
        :param extra_button: Доп кнопки.
        :param width: Ширина.
        :param height: Высота.
        :param timeout: Время задержки отображения.

        :return None.
        """
        super().__init__(self.ZENITY_CMD)
        self.title = title
        self.ok_label = ok_label
        self.cancel_label = cancel_label
        self.extra_button = extra_button
        self.width = width
        self.height = height
        self.timeout = timeout
        self._method_count_param: dict[str, bool] = {}
        self.req_forms_fields: None | tuple[str, ...] = None

        self._throw_general_args(
            zen_params={
                "title": title,
                "extra_button": extra_button,
                "ok_label": ok_label,
                "width": width,
                "height": height,
                "timeout": timeout,
            }
        )

    @staticmethod
    def __check_zen_param(method: Callable[..., Any]) -> Callable[..., Any]:
        """
        Декоратор для `ограничения` использования несовместимых аргументов класса Zenity.

        Если метод вызван впервые, добавляет в выражение для исполнения основной аргумент.
            *Example*: ``--info --list ...``

        Имя аргумент берётся из названия метода.
            *Example*: ``throw_forms_args`` -> ``forms``
        """

        @wraps(method)
        def wrapper(self: Zenity, *args, **kwargs) -> Callable[..., Any]:
            method_name: str = method.__name__
            if self._method_count_param.get(method_name):
                raise AttributeError(f"Метод <{method_name}> вызван несколько раз!")
            else:
                self._method_count_param[method_name] = True
                self._expression.insert(1, f"--{method_name.lstrip("_").split("_")[1]}")
            return method(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def __validate_list_columns(columns: FormsFields) -> bool:
        if len(set(map(len, columns.values()))) > 1:
            return False
        return True

    def __get_forms_field_params(self, forms_params: FormsFields | None, command_name: str, raw_params: T = None) -> T:
        if command_name not in self.FORMS_FIELDS_NAME.values():
            raise ApplicationException(
                f"Передан неверное поля формы - <{command_name}>. "
                f"Допустимые поля [{cust_join(tuple(self.FORMS_FIELDS_NAME.values()))}]"
            )
        if raw_params is None:
            raw_params = ()
        if forms_params is None:
            forms_params = {}
        for param_name, param_values in forms_params.items():
            raw_params += (
                f"--add-{command_name}={param_name}",
                f"--{command_name}-values={cust_join(param_values, "|")}"
            )
        return raw_params

    def _throw_general_args(self, zen_params: dict[str, str | int]) -> None:
        """
        Применение базовых аргументов команды для исполнения.

        :param zen_params: Параметры базовых аргументов (ZENITY_ARGS).

        :return None.
        """
        insert_index = 1

        for kwarg in zen_params:
            command = self.ZENITY_ARGS.get(kwarg)
            if not command:
                raise AttributeError(EXCEPTIONS["zen_atr"].format(kwarg))
            else:
                if zen_params[kwarg]:
                    zen_cmd = command(zen_params[kwarg])
                    if isinstance(zen_params[kwarg], (list, set, tuple)):
                        for cmd in zen_cmd:
                            self._expression.insert(insert_index, cmd)
                    else:
                        self._expression.insert(insert_index, zen_cmd)

    def throw_icon(self, icon: str, do_global: bool = False) -> None:
        if do_global:
            self.ICON = icon
        self._throw_general_args(zen_params={"icon": self.ICON})

    @__check_zen_param
    def throw_question_args(self, text: str) -> None:
        self._expression.append(self.ZENITY_ARGS["text"](text))

    @__check_zen_param
    def throw_info_args(self, text: str) -> None:
        """
        Применение информационных аргументов команды для исполнения.

        :param text: Текст информационного окна.

        :return: Статус применения.
        """
        self._expression.append(self.ZENITY_ARGS['text'](text))

    @__check_zen_param
    def throw_forms_args(self, entry: FormsValues = None, text: str = "", req_entry: FormsValues = None,
                         combos: FormsFields = None, selection: FormsFields = None, calender_name: str | None = None,
                         data_and_time: bool = False, calender_format: str = "%Y-%m-%d") -> None:
        """
        Применение аргументов формы команды для исполнения.
            Аннотация типа **FormsValues** обозначает - `(ключ - название поля, значение - элементы этого поля)`.

        :param text: Название формы.
        :param entry: Поля для ввода (не обязательные).
        :param req_entry: Поля для ввода (обязательные).
        :param combos: Выпадающий список (1 элемент выбран сразу).
        :param selection: Список элементов для выбора.
        :param calender_name: Имя поля для выбора даты.
        :param data_and_time: Добавить ли поле для ввода времени.
        :param calender_format: Формат вывода времени.

        :return: None
        """
        if req_entry:
            text += ZENITY["req_fields"]

        req_entry = self.ZENITY_ARGS['req_entry'](req_entry)

        self._expression.extend([
            self.ZENITY_ARGS["text"](text),
            *req_entry,
            *self.ZENITY_ARGS["entry"](entry),
            *self.__get_forms_field_params(forms_params=combos, command_name=self.FORMS_FIELDS_NAME[1]),
            *self.__get_forms_field_params(forms_params=selection, command_name=self.FORMS_FIELDS_NAME[2]),
        ])
        if calender_name:
            calender = self.ZENITY_ARGS["calender"](calender_name)
            if data_and_time:
                self._expression.extend([
                    calender,
                    *self.ZENITY_ARGS["entry"](("Время (Часы:Минуты:Секунды)",))
                ])
            else:
                self._expression.append(calender)
            self._expression.append(f"--forms-date-format={calender_format}")

    @__check_zen_param
    def throw_list_args(self, columns: FormsFields, return_column_number: int = 0, checklist: bool = False,
                        radiolist: bool = False, edit: bool = False, ) -> None:
        """

        :param columns: Тело таблицы.
        :param return_column_number: Номер возвращаемого столбца.
        :param checklist: Возможность выбрать все строки.
        :param radiolist: Возможность выбрать только одну строку.
        :param edit: Возможность редактировать поля таблицы.

        :return: Столбец таблицы под номером указанном в ``return_column_number`` или `все` столбцы выбранных строк(и).
        """

        columns_values = tuple(columns.values())
        table_column_count = len(columns_values[0])
        row_count = len(columns_values)
        if radiolist and checklist:
            raise ArgsException(args=("checklist", "radiolist"))
        elif (checklist and row_count <= 1) or (radiolist and row_count <= 1):
            raise ArgsException(
                args=("checklist", "radiolist"),
                msg="Невозможно указать данные аргументы с количество столбцов менее 1!",
            )

        if return_column_number > table_column_count:
            raise ArgsException(
                msg=ZENITY["columns"].format(
                    returned_column=return_column_number,
                    len_list_values=table_column_count
                ),
                args=("columns",))

        assert self.__validate_list_columns(columns), ZENITY["len_columns"]

        return_column_number = "ALL" if return_column_number <= 0 else str(return_column_number)

        expr = []
        (
            expr.append("--checklist") if checklist else None,
            expr.append("--radiolist") if radiolist else None,
            expr.append("--editable") if edit else None,
            expr.append(f"--print-column={return_column_number}"),
        )
        self._expression.extend(expr)
        del expr

        self._expression.extend([f"--column={column}" for column in columns])

        index = 0
        while table_column_count:
            for column in columns_values:
                value = column[index]
                self._expression.append(value)
            index += 1
            table_column_count -= 1

    @__check_zen_param
    def throw_entry_args(self, entry_description: str = "", entry_text: tuple[str, ...] = None,
                         hide_entries: bool = False) -> None:
        """
        Применение аргументов окна для ввода данных в указанное поле `entry_name`.

        :param entry_description: Описание поля для ввода.
        :param entry_text: Список вариантов поля.
        :param hide_entries: Скрыть вводимые данные. (Отключает ``entry_text``)

        :return: Введенные данные в поле ``entry_name``.
        """
        if hide_entries:
            self._expression.append("--hide-text")
        self._expression.extend([
            self.ZENITY_ARGS["text"](entry_description),
            "" if not entry_text else f"--entry-text",
        ])
        if entry_text is not None:
            for entry in entry_text:
                self._expression.append(entry)

    @__check_zen_param
    def throw_error_args(self, error_msg: str = "") -> None:
        """
        Применение аргументов сообщения об ошибке.
        
        :param error_msg: Тело сообщения об ошибке.
        
        :return: Сообщение об ошибке аргумента ``error_msg``.
        """

        if "\n" in error_msg and not any((self.height, self.width)):
            self.width = 300
            self._throw_general_args({"width": self.width})
        self._expression.append(self.ZENITY_ARGS["text"](error_msg))

    async def do_notify(self, task_name: None | str = None, command: list[str] | None = None,
                        communicate: bool = True, ignore_error: bool = False) -> ProcessResult:
        return await self.exec_subprocess(
            tsk=task_name if task_name else io.current_task(),
            cmd=command or self._expression,
            interplay=communicate,
            ignore_error=ignore_error,
        )
