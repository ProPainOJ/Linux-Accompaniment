# !/usr/bin/python3
import asyncio as io
import time
from datetime import datetime
from functools import partial
from queue import Queue
from typing import Callable, Coroutine

from bson import ObjectId
from pynput.keyboard import Key, GlobalHotKeys, KeyCode
from sqlalchemy import Sequence
from sqlalchemy.orm import InstrumentedAttribute
from typing_extensions import TypeVar

from database.dto.dto import Category, Reminder
from database.dto.dto_mongo import BaseNotification, CreateNotification, SetNotificationDTO
from database.repositiry.base import FullDBObjectNotification
from database.repositiry.mixed_rep import MixedRepository
from database.repositiry.mongo_rep import NotificationsRepository
from database.repositiry.postgres_rep import ReminderRepository
from exceptions.zenity import AbortZenityInsert
from notification.base import ShellExec, ProcessResult
from notification.notify import Notify
from notification.zenity import Zenity, FormsValues, FormsValue
from property.constants import INFO, ZENITY_FORMS_FIELDS, ZENITY, EXCEPTIONS, NotifyUrgency
from property.helpers import cust_join, get_hotkey, get_key_dict_by_value
from property.settings import Settings

Q = TypeVar("Q", bound=bool)


class App:
    ACTIONS: dict = {
        "open": "open_url",
        "show": "show",
        "remind": "remind",
    }

    def __init__(self) -> None:
        self.settings: Settings = Settings()
        self.shell = ShellExec()
        self.check_hotkey: bool = True
        self.menu_action: dict[str, Callable[[], Coroutine]] = {
            "create": self.create_new_notify,
            "show": self.show_notifies,
            "show_filter": ...,
            "delete": self.delete_notify,
        }

    @staticmethod
    async def __create_new_notify(new_notify_value: FullDBObjectNotification) -> None:
        new_notify = []
        create_new_obj = Notify(
            title="Создано новое уведомление!",
            text=f"Уведомление: `{new_notify_value.postgres_notify.name}` было успешно создано.",
            urgency=NotifyUrgency.LOW,
        )

        try:
            new_notify = await NotificationsRepository().create_objects([new_notify_value.mongo_notify])
            new_notify_value.postgres_notify.mongo_uuid = str(new_notify.inserted_ids[0])
            new_notify_post = io.create_task(ReminderRepository().create_objects([new_notify_value.postgres_notify]))
            new_notify_post.add_done_callback(
                lambda _: io.create_task(create_new_obj.do_notify(communicate=False, ignore_error=True))
            )
        except BaseNotification:  # type: ignore
            if new_notify:
                deleted_object = io.create_task(NotificationsRepository().delete_objects(new_notify))
                _print = partial(print, f"Удаление {new_notify} прервано!")
                deleted_object.add_done_callback(_print)

    @staticmethod
    async def _create_menu_queue(str_keys: str) -> tuple[Queue[Q], GlobalHotKeys]:
        """Создание очереди на открытие меню.

        :param str_keys: Строка с сочетанием горячих клавиш в читаемом формате для `pynput`.

        :return: Очередь с флагами на открытие меню приложения.
        """
        queue: Queue[Q] = io.Queue()
        current_loop = io.get_running_loop()
        cancel_hot_key = (Key.ctrl, Key.alt, KeyCode.from_char("l"), Key.esc,)
        str_cancel_hot_key = get_hotkey(cancel_hot_key)

        def throw_flag_queue(str_hotkey: str, flag: bool = True, ):
            print(f"Была нажата комбинация [{str_hotkey}]!")
            if flag is False:
                print(f"Прослушивание {str_keys} остановлено!")
            current_loop.call_soon_threadsafe(queue.put_nowait, flag)

        hot_kay_listener = GlobalHotKeys({
            str_keys: partial(throw_flag_queue, str_keys, True),
            f"{str_cancel_hot_key}": partial(throw_flag_queue, f"{str_cancel_hot_key}", False),
        })
        hot_kay_listener.start()
        print(f"Начал слушать [{str_keys}]")

        return queue, hot_kay_listener

    @staticmethod
    async def get_data_in_loop(
            zenity_forms: Zenity,
            get_field: FormsValues,
            forms_text: str = ""
    ) -> dict[FormsValue, str] | None:
        """Запрос формы с полями для ввода данных от пользователя `Zenity`.

        :param zenity_forms: Объект `Zenity` с указанными параметрами окна.
        :param get_field: Поля для ввода.
        :param forms_text: Дополнительный текст формы.

        :raise AbortZenityInsert: Если пользователь отменил ввод данных.

        :return: Словарь с именами полей и их значениями.
        """

        new_entry_values = {entry: "" for entry in get_field}
        get_new_data_flag = True
        while get_new_data_flag:
            zenity_forms = Zenity(title=zenity_forms.title, width=zenity_forms.width, height=zenity_forms.height)
            zenity_forms.throw_forms_args(
                req_entry=tuple(
                    ZENITY_FORMS_FIELDS[field] if ZENITY_FORMS_FIELDS.get(field) else field for field in get_field
                ),
                text=forms_text
            )

            get_zen_data = await zenity_forms.do_notify()

            if get_zen_data.code != 0:
                raise AbortZenityInsert

            get_new_data_flag = False
            empty_fields = ()
            for value_index, field_value in enumerate(get_zen_data.out.split("|")):
                if field_value:
                    new_entry_values[get_field[value_index]] = field_value
                else:
                    get_new_data_flag = True
                    empty_fields += (get_field[value_index],)

            if get_new_data_flag:
                z = Zenity(title=EXCEPTIONS["zen_input_field"], timeout=2)
                z.throw_error_args(
                    error_msg=f"Не были введены или введены неверно следующие поля:\n{cust_join(
                        [
                            f"{i}. <b>{ZENITY_FORMS_FIELDS[field].capitalize()}</b>"
                            if ZENITY_FORMS_FIELDS.get(field) else
                            f"{i}. <b>{field.capitalize()}</b>"
                            for i, field in enumerate(empty_fields, start=1)
                        ],
                        "\n"
                    )}"
                )
                await z.do_notify()
                get_field = empty_fields

        return new_entry_values

    async def __validate_time_notify(self, _data: str, _format: str, get_time: bool = True):
        while True:
            try:
                _data = datetime.strptime(_data, _format)
            except ValueError:
                field = "Время" if get_time else "Дата"
                _data = await self.get_data_in_loop(
                    Zenity(EXCEPTIONS["zen_input_field"]),
                    get_field=(field,),
                    forms_text=ZENITY["data"]["data"].format(accept_format=_format)
                    if get_time else ZENITY["data"]["time"].format(_format),
                )
                _data = _data[field]
            else:
                break

        return _data.time() if get_time else _data.date()

    async def _validate_new_notify(self, new_task_notify: io.Task,
                                   req_entry: dict[str, str]) -> FullDBObjectNotification:

        new_notification_result: ProcessResult = await new_task_notify

        if new_notification_result.code == 1:
            raise AbortZenityInsert
        task_result: str = new_notification_result.out

        req_entry_index = len(req_entry)
        empty_req_entry = ()
        new_notification_value = {}
        new_notification_values = task_result.split("|")

        for value_index, entry in enumerate(ZENITY_FORMS_FIELDS):
            if req_entry_index > 0 and not new_notification_values[value_index]:
                empty_req_entry += (entry,)
            else:
                new_notification_value |= {entry: new_notification_values[value_index]}
            req_entry_index -= 1

        if empty_req_entry:
            new_field_value = await self.get_data_in_loop(
                Zenity(title="Обязательные поля были не введены!"),
                empty_req_entry
            )
            if new_field_value is None:
                raise AbortZenityInsert
            new_notification_value |= new_field_value

        if self.ACTIONS["open"] in new_notification_value["action"]:
            new_notification_value |= {"extra_args": await self.get_data_in_loop(
                Zenity(
                    title=ZENITY["url"]["title"],
                    width=400,
                    height=125,
                ),
                ("url",),
                forms_text=ZENITY["url"]["forms_text"],
            )}
        new_reminder = Reminder()
        for field_name, field_value in new_notification_value.copy().items():
            if field_name == "name":
                new_reminder.name = field_value
            elif field_name == "time":
                new_reminder.target_time = await self.__validate_time_notify(_data=field_value, _format="%H:%M:%S")
            elif field_name == "data":
                new_reminder.target_data = datetime.strptime(new_notification_value["data"], "%Y-%m-%d").date()
            else:
                continue
            del new_notification_value[field_name]

        return FullDBObjectNotification(new_reminder, CreateNotification(SetNotificationDTO(**new_notification_value)))

    async def create_new_notify(self) -> None:
        notify_category = await ReminderRepository().get_by_filter_by(stmt=Category)
        new_zen_notify = Zenity(title="Создание нового уведомления", ok_label="Создать")
        req_entry = {ZENITY_FORMS_FIELDS["name"]: "", ZENITY_FORMS_FIELDS["title"]: ""}
        new_zen_notify.throw_forms_args(
            req_entry=tuple(key for key in req_entry.keys()),
            entry=(ZENITY_FORMS_FIELDS["description"],),
            combos=({
                ZENITY_FORMS_FIELDS["action"].capitalize(): BaseNotification.AVAILABLE_ACTION,
            }),
            selection={
                ZENITY_FORMS_FIELDS["category"].capitalize(): [category.name for category in notify_category]
            },
            calender_name=ZENITY_FORMS_FIELDS["data"].capitalize(),
            data_and_time=True,
        )

        new_mongo_notify = await self._validate_new_notify(
            new_task_notify=io.create_task(new_zen_notify.do_notify()),
            req_entry=req_entry,
        )

        await self.__create_new_notify(new_mongo_notify)

    async def delete_notify(self) -> None:
        choose_notify = Zenity(title="Поиск уведомлений")
        choose_notify.throw_question_args(text="Совершить поиск по параметрам уведомления?")
        all_notify = await choose_notify.do_notify()

        if all_notify.code:
            reminder_list = await MixedRepository().get_by_filters({})
        else:
            notify_name = await self.get_data_in_loop(
                zenity_forms=Zenity("Поиск уведомления"),
                get_field=(ZENITY_FORMS_FIELDS["name"],),
                forms_text="Выберите фразу для поиска уведомления по имени."
            )
            reminder_list = await MixedRepository().get_by_filters({
                Reminder.name: notify_name[ZENITY_FORMS_FIELDS["name"]]
            })
            if not reminder_list:
                no_data = Zenity("Поиск уведомления", timeout=5)
                no_data.throw_info_args(
                    f"Не было найдено уведомлений по паттерну {notify_name[ZENITY_FORMS_FIELDS["name"]]}"
                )
                await io.gather(no_data.do_notify(), self.delete_notify())
                return
        # await self.show_notifies(reminder_list)

    async def get_chosen_notify(
            self,
            zenity_window: Zenity | None = None,
            chosen_objects: Sequence[Reminder] | None = None,
            show_fields: dict[InstrumentedAttribute[str], str] | None = None,
            **zenity_list_args,
    ) -> tuple[FullDBObjectNotification]:
        if show_fields is None:
            show_fields = {
                Reminder.mongo_uuid: "🚩",
                Reminder.name: "Название",
                Reminder.target_data: "📆",
                Reminder.target_time: "⏰",
                Reminder.status: "✅",
            }
        if zenity_window is None:
            zenity_window = Zenity(
                title="Список напоминаний",
                ok_label="Просмотреть выбранное",
                width=1000,
                height=500,
            )
        if chosen_objects is None:
            chosen_objects = await ReminderRepository().get_by_filter_by()
        if not zenity_list_args:
            zenity_list_args = {"radiolist": True, "return_column_number": 1}

        columns = {window_name: tuple() for window_name in show_fields.values()}

        full_notifies = {}
        for reminder in chosen_objects:
            mongo_uuid = ObjectId(reminder.mongo_uuid)
            full_notifies[mongo_uuid] = FullDBObjectNotification(reminder, mongo_notify=None)

            for notification_attr, window_attr_name in show_fields.items():
                columns[window_attr_name] += (str(reminder.__getattribute__(notification_attr.key)),)

        zenity_window.throw_list_args(
            columns=columns,
            **zenity_list_args,
        )

        while True:
            mongo_uuids = await zenity_window.do_notify()
            if mongo_uuids.code:
                raise AbortZenityInsert
            if mongo_uuids.out:
                mongo_uuids = mongo_uuids.out.split("|")
                break

        i = 0
        rem_mongo_uuids = []
        column_counter = len(columns) - 1
        column_names = tuple(columns.keys())
        for index, notify_value in enumerate(mongo_uuids):
            if "return_column_number" in zenity_list_args:
                return_index = zenity_list_args["return_column_number"]
                if return_index == index:
                    notification_attr = get_key_dict_by_value(show_fields, column_names[return_index])
                    if notification_attr is Reminder.mongo_uuid:
                        pass
                    break
                continue
            rem_mongo_uuids.append(column_names[i])
            if i == column_counter:
                i = 0
            else:
                i += 1
        if "return_column_number" not in zenity_list_args:
            notifications = await NotificationsRepository().get_by_filter(filters={"_id": {"$in": rem_mongo_uuids}})

        rem_mongo_uuids = ()
        for notify in notifications:
            full_notify = full_notifies[notify.notify["_id"]]
            full_notify.mongo_notify = notify

            rem_mongo_uuids += (full_notify,)

        return rem_mongo_uuids

    async def show_notifies(self, list_rem: Sequence[Reminder] = None) -> None:
        await self.get_chosen_notify(radiolist=True)

        if list_rem is None:
            list_rem = await ReminderRepository().get_by_filter_by()

        columns = {name: tuple() for name in ("🚩", "name", "📆", "⏰", "✅")}

        for reminder in list_rem:
            columns["🚩"] += (str(reminder.mongo_uuid),)
            columns["name"] += (str(reminder.name),)
            columns["📆"] += (str(reminder.target_data),)
            columns["⏰"] += (str(reminder.target_time),)
            columns["✅"] += (str(reminder.status),)

        list_zen_notify = Zenity(
            title="Список напоминаний",
            ok_label="Просмотреть выбранное",
            width=1000,
            height=500,
        )

        list_zen_notify.throw_list_args(columns=columns.copy(), return_column_number=1, radiolist=True)
        notify_action = await list_zen_notify.do_notify()

        if notify_action.code == 1 and not notify_action.out:
            return

        mongo_bodies = await NotificationsRepository().get_by_filter(
            filters={
                "_id": {
                    "$in": list((map(ObjectId, notify_action.out.split('|'))))
                }
            }
        )
        mongo_zen_body = Zenity("Список уведомлений")
        mongo_zen_body.throw_info_args(mongo_bodies[0]["description"])
        io.create_task(mongo_zen_body.do_notify())
        print(mongo_bodies)

    async def show_menu_notify(self) -> None:
        """Показать уведомление.

        :return: None
        """
        notify = Zenity(title=str(self.settings.app_name), timeout=15)
        notify.throw_question_args(text="Открыть меню редактора напоминаний?")
        menu_result: ProcessResult = await notify.do_notify(communicate=True)

        if menu_result.code == 0:
            z = Zenity(title=self.settings.app_name, width=960, height=540)
            z.throw_list_args(
                text="Выберите действие из списка",
                columns=ZENITY["menu"]["column_list"],
                radiolist=True,
                return_column_number=1,
            )
            menu_action = await z.do_notify(communicate=True, ignore_error=True)
            while not menu_action.out:
                if menu_action.code == 1:
                    raise AbortZenityInsert
                menu_action = await z.do_notify(communicate=True, ignore_error=True)
            if not self.menu_action.get(menu_action.out):
                raise NotImplementedError(f"Не создано действие меню для {menu_action.out}")
            await self.menu_action[menu_action.out]()

    async def do_notify_tasks(self, notices: list[dict]):
        for nf in notices:
            for action in nf["action"]:
                if action == self.ACTIONS["open"]:
                    io.create_task(self.shell.open_browser_url(url=nf["url"]))

                if action == self.ACTIONS["show"]:
                    zen_msg = Zenity(title=nf["title"], timeout=10)
                    zen_msg.throw_info_args(text=nf.get("description") or "<3")
                    io.create_task(zen_msg.do_notify(communicate=True))

                if action == self.ACTIONS["remind"]:
                    pass

    async def catch_menu_trigger(
            self, hotkey: tuple[Key | str, ...] = (Key.ctrl, Key.alt, KeyCode.from_char("l"), KeyCode.from_char("a"))
    ) -> None:
        """Отлавливает нажатие горячих клавиш `hotkey` для открытия меню приложения.

        :param hotkey: Комбинация горячих клавиш.

        :return: None
        """
        queue, listener = await self._create_menu_queue(get_hotkey(hotkey))

        print(f"Статус потока - {listener.is_alive()}")
        while listener.is_alive():

            flag = await queue.get()
            if flag:
                try:
                    await self.show_menu_notify()
                except AbortZenityInsert:
                    if self.settings.debug:
                        print(AbortZenityInsert.__name__)
                except Exception as e:
                    raise e
                finally:
                    while not queue.empty():
                        queue.get_nowait()
                        queue.task_done()
            elif not flag:
                listener.stop()
        else:
            print("Не должен тут быть!")
        return


async def main(app: App = App()) -> None:
    """Старт приложения."""
    task = io.create_task(app.catch_menu_trigger())
    task.set_name(f"{app.catch_menu_trigger.__name__}")
    print(f"Создание задачи <{task.get_name()}>")
    while not task.done():
        await io.sleep(5, print("Спал 5 секунд!"))
    # await app.delete_notify()


if __name__ == "__main__":
    time_start = time.time()
    loop = io.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        time_end = time.time()
        print(INFO["end_info"].format(
            time_min=round((time_end - time_start) / 60, 2),
            time_sec=round(time_end - time_start, 3)
        ))
