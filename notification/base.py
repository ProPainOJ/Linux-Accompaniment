import asyncio as io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from subprocess import SubprocessError

from property.constants import EXCEPTIONS
from property.helpers import cust_join
from property.settings import Settings

type processes_dict = dict[str, ProcessBody]


@dataclass
class ProcessResult:
    code: int | None = None
    out: str | int | None = None
    error: str | None = None

    def __repr__(self) -> str:
        """:return: id(self) code: [<error>|<out>]"""
        return f"{id(self)}: {self.code} [<{self.error}>|<{self.out}>]"


@dataclass
class ProcessBody:
    """Дата класс результатов исполняемых процессов."""
    process: io.subprocess.Process
    result: ProcessResult = ProcessResult


class ShellExec:
    RESULT = ProcessBody
    GNOME_BROWSER = "gnome-www-browser"
    PROCESSES_RESULT: processes_dict = {}

    async def exec_subprocess(
            self, cmd: list[str], tsk: io.Task | None = None, interplay: bool = False, ignore_error: bool = False
    ) -> ProcessResult:
        """
        Исполняет выражение CMD.

        :param cmd: Выражение для исполнения.
        :param tsk: Задача для выполнения cmd.
        :param interplay: Необходимость ожидания ответа терминала.
        :param ignore_error: Необходимость игнорировать ошибки от терминала (только с interplay).

        :return: Код ответа терминала, Текстовый отвела, Сообщение об ошибке.
        """
        tsk_name = io.current_task().get_name() if not tsk else tsk.get_name()

        process = await io.create_subprocess_exec(
            *cmd,
            stdout=None if not interplay else io.subprocess.PIPE,
            stderr=None if not interplay else io.subprocess.PIPE,
        )

        self.PROCESSES_RESULT[tsk_name] = self.RESULT(process)
        current_task_result = self.PROCESSES_RESULT[tsk_name].result

        if interplay:
            await process.wait()
            out, err = await process.communicate()

            current_task_result.out, current_task_result.error = out.decode().rstrip("\n"), err.decode()
            self.PROCESSES_RESULT[tsk_name].result.code = process.returncode

            if current_task_result.error and not ignore_error:
                raise SubprocessError(EXCEPTIONS["communicate"].format(err, expr=cust_join(cmd)))

            print(tsk_name, ">>>", self.PROCESSES_RESULT[tsk_name].process)

        return current_task_result

    async def open_browser_url(self, url: str):
        io.create_task(self.exec_subprocess(cmd=[self.GNOME_BROWSER, "--new-window", url]))


class BaseNotify(ABC, ShellExec):
    """Касс для реализации уведомления в Linux."""
    APP_NAME: str = Settings().app_name

    def __init__(self, start_expr: str) -> None:
        """
        Init базовых настроек уведомлений.

        :param start_expr: Начало команды (название утилиты) для исполнения в терминале.

        :return: None.
        """
        self._expression: list[str] = [start_expr]
        self.settings: Settings = Settings()

    @abstractmethod
    async def do_notify(self, task_name: None | str = None, command: None | list[str] = None,
                        communicate: bool = True, ignore_error: bool = False) -> ProcessResult:
        """
        Реализации и обработка результата уведомления.

        :param task_name: Имя задачи.
        :param command: Параметры для исполнения команды в терминале.
        :param communicate: Необходимость ожидания ответа.
        :param ignore_error: Игнорировать тело ошибки при выполнении командной строке.

        :return Код ответа, Тело ответа, Тело ошибки.
        """
        pass
