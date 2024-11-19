from notification.base import BaseNotify, ProcessResult
from property.constants import NotifyUrgency


class Notify(BaseNotify):
    NOTIFY_CMD = "notify-send"

    def __init__(self, title: str, text: str, urgency: NotifyUrgency = NotifyUrgency.LOW) -> None:
        super().__init__(self.NOTIFY_CMD)
        self.urgency = urgency
        self.title = title
        self.text = text
        self._expression.extend(("-u", self.urgency, self.title, self.text))

    def throw_extra_buttons(self, buttons: tuple[tuple[int, str], ...]) -> None:
        """Добавление кнопок действий на уведомление.

        :param buttons: Tuple id кнопок и их имён.
        :return: None.
        """
        for btn in buttons:
            self._expression.extend(("--action", f"{btn[0]}={btn[1]}"))

    async def do_notify(self, task_name: None | str = None, command: None | list[str] = None,
                        communicate: bool = False, ignore_error: bool = True) -> ProcessResult:
        process_result = await self.exec_subprocess(
            self._expression,
            interplay=communicate,
            ignore_error=ignore_error
        )
        return process_result
