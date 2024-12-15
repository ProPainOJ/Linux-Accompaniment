from property.patterns import BaseEnum


class AppMenuAction(BaseEnum):
    """Имена действий в меню приложений."""
    create: str = "создать"
    show: str = "просмотр"
    delete: str = "удалить"
    del_all: str = "удалить все‼"
    update: str = "обновить"
    conform: str = "подтвердить"


NOTIFICATIONS: dict[str, str] = {
    "time_break": "Пора сделать перерыв для глаз!\nПрошло ({0}) мин. Время рабочей сессии (~{1} час.)"
}
EXCEPTIONS: dict[str, str] = {  # Ошибки.
    "wrong_expr": "Неверная формулировка выражения для выполнения!",
    "zen_atr": "Передан неверный атрибут ({0}) для исполнения Zenity!",
    "communicate": "Ошибка при выполнении подпроцесса <{0}>!\n Выражение для исполнения <[{expr}]>",
    "level_urg": "Указан неверный уровень отображения уведомления Notify - <{0}>. Доступные уровни <[{1}]>!",
    "zen_info": "Переданный неверный аргумент(ы) Zenity! Аргументы: <[{}]>!",
    "settings_file_exist": "Файл с настройками <{file_name}> был перемещён/удалён/переименован! "
                           "Также, возможно, {settings_class_name} был вызван не из точки входа приложения <main.py>.\n"
                           "Попытка найти файл по пути {set_path}.",
    "zen_input_field": "Ошибка ввода полей!",
}
INFO = {
    "settings_db_url": "INFO >>> Создана ссылка для подключения к {db_type}: {url}",
    "end_info": "Работа приложения продолжалась {time_min} минут ({time_sec} секунд)!"
}

ZENITY = {  # Поля и др. константы окон Zenity.
    "req_fields": "<span color='grey' font='10'><i>\nПоля отмеченные '*'</i><span color='white' font='10'> <b> обязательны</b></span> <i>для заполнения</i></span>",
    "columns": "Передано неверный номер столбца для возвращения - {returned_column}."
               " При данных параметрах доступно отображение 1-{len_list_values} столбца!",
    "len_columns": "Количество значений в строке таблицы не соответствует количеству столбцов в этой таблице!",
    "data": {
        "data": "Введенная дата введена в неверном формате. Допустимый формат {accept_format}",
        "time": "Введенное время указано в неверном формате. Допустимый формат {accept_format}",
    },
    "url": {
        "title": "Был указан параметр open_url. Укажите ссылку для уведомления.",
        "forms_text": "URL ссылка формата: <span color='gold'><b>https://www.google.com/</b></span>",
    },
    "menu": {
        "column_list": {
            "": (
                AppMenuAction.create.name,
                AppMenuAction.show.name,
                AppMenuAction.update.name,
                AppMenuAction.delete.name
            ),
            "Действие": (
                AppMenuAction.create.capitalize(),
                AppMenuAction.show.capitalize(),
                AppMenuAction.update.capitalize(),
                AppMenuAction.delete.capitalize(),
            ),
            "Описание": (
                "Создание нового напоминания",
                "Просмотр всех созданных напоминаний",
                "Обновление ваших напоминаний",
                "Удаление уведомлений по фильтру и т.д."
            ),
        }
    },
}

ZENITY_FORMS_FIELDS: dict[str, str] = {  # Список полей для ввода формы уведомления.
    "name": "название",
    "title": "заголовок",
    "description": "описание",
    "action": "действие",
    "category": "категория",
    "data": "дата напоминания",
    "time": "время",
}


class NotifyUrgency(BaseEnum):
    LOW: str = "low"
    NORMAL: str = "normal"
    CRIT: str = "critical"
