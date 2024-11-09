import configparser
import os.path

from exceptions.app import ApplicationException
from exceptions.database import ConfigException
from property.constants import EXCEPTIONS, INFO
from property.patterns import Singleton


class Settings(Singleton):
    """Настройки приложения."""

    SETTING_FILE_NAME = "settings.ini"
    SETTINGS_PATH = os.path.join("..", SETTING_FILE_NAME)
    CONFIG = None

    def __init__(self) -> None:
        if not self.CONFIG:
            self.CONFIG = self.__get_config_file()
        self.debug = bool(self.CONFIG.get("ALL", "DEBUG"))
        if self.debug:
            self._app_dir = self.CONFIG.get("DEV", "APP_PATH")
            self._time_end = self.CONFIG.get("DEV", "BREAK_TIME")
            self._app_name = self.CONFIG.get("DEV", "NAME")
            self._log_name = self.CONFIG.get("DEV", "LOG_NAME")
            self._error_log_name = self.CONFIG.get("DEV", "ERROR_LOG_NAME")
        else:
            self._app_dir = self.CONFIG.get("APP", "APP_PATH")
            self._time_end = self.CONFIG.get("APP", "BREAK_TIME")
            self._app_name = self.CONFIG.get("APP", "NAME")
            self._log_name = self.CONFIG.get("APP", "LOG_NAME")
            self._error_log_name = self.CONFIG.get("APP", "ERROR_LOG_NAME")

    def __get_config_file(self) -> FileExistsError | configparser.ConfigParser:
        if not os.path.exists(self.SETTINGS_PATH):
            raise FileExistsError(
                EXCEPTIONS["settings_file_exist"].format(
                    file_name=self.SETTING_FILE_NAME,
                    settings_class_name=self.__class__.__name__,
                    set_path=self.SETTINGS_PATH,
                ))

        config = configparser.ConfigParser()
        config.read(self.SETTINGS_PATH)
        return config

    @property
    def time_end(self) -> int:
        """Время одного периода работы."""
        return int(self._time_end)

    @property
    def app_name(self) -> str:
        """Названия приложения."""
        return self._app_name.strip('"')

    @property
    def log_name(self) -> str:
        """Название файла логгирования."""
        return self._log_name

    @property
    def error_name(self) -> str:
        """Название файла логгирования ошибок."""
        return self._error_log_name

    @property
    def app_dir(self) -> str:
        """Путь приложения."""
        return self._app_dir

    @property
    def dir_log_name(self) -> str:
        """Путь к файлу логгирования."""
        return self._app_dir + self._log_name

    @property
    def dir_error_name(self) -> str:
        """Путь к файлу логгирования ошибок."""
        return self._app_dir + self._error_log_name

    @property
    def dir_app_name(self) -> str:
        """Путь к приложению."""
        return self._app_dir + self.app_name


class DataBaseSettings(Settings):
    DB_TYPES = ('postgres', 'mongo')
    LOCAL_HOST = "localhost"
    DEFAULT_DB_URL = {
        "postgres": {
            "HOST": LOCAL_HOST,
            "PORT": 5432,
        },
        "mongo": {
            "HOST": LOCAL_HOST,
            "PORT": 27017,
        }
    }

    def __init__(self) -> None:
        super().__init__()
        self._name = self.CONFIG.get("DB", "DB_NAME")
        self._name_mongo = self.CONFIG.get("DB", "DB_NAME_MONGO")

        self._user = self.CONFIG.get("DB", "DB_USER")
        self._user_mongo = self.CONFIG.get("DB", "DB_USER_MONGO")

        self.__password = self.CONFIG.get("DB", "DB_PASSWORD")
        self.__password_mongo = self.CONFIG.get("DB", "DB_PASSWORD_MONGO")

        self.type = self.CONFIG.get("DB", "DB_TYPE")
        self.type_mongo = self.CONFIG.get("DB", "DB_TYPE_MONGO")

        self.__host = self.CONFIG.get("DB", "DB_HOST") or self.DEFAULT_DB_URL["postgres"]["HOST"]
        self.__port = self.CONFIG.get("DB", "DB_PORT") or self.DEFAULT_DB_URL["postgres"]["PORT"]
        self.__host_mongo = self.CONFIG.get(
            "DB", "DB_HOST_MONGO"
        ) or self.DEFAULT_DB_URL["mongo"]["HOST"]
        self.__port_mongo = self.CONFIG.get(
            "DB", "DB_PORT_MONGO"
        ) or self.DEFAULT_DB_URL["mongo"]["PORT"]

        self.echo = True if self.debug else False

        self.__create_database_url(db_type="postgres")
        self.__create_database_url(db_type="mongo")

    def __create_database_url(self, db_type: str) -> None | ApplicationException:
        """Создание ссылки подключения для баз данных.

        :param db_type: Название базы данных для создания url-подключения.
        :return: None.
        """
        if db_type not in self.DB_TYPES:
            raise ConfigException(
                f"Выбран неверный тип бд для подключений <{db_type}>! Доступные параметры - [{", ".join(self.DB_TYPES)}]"
            )
        if db_type == self.DB_TYPES[0]:
            self.__postgres_url = f"postgresql+asyncpg://{self._user}:{self.__password}@{self.__host}:{self.__port}/{self._name}"
            if self.debug and self.FIRST_START:
                print(INFO["settings_db_url"].format(db_type=db_type, url=self.__postgres_url))
            return
        if db_type == self.DB_TYPES[1]:
            self.__mongo_url = f"mongodb://{self._user_mongo}:{self.__password_mongo}@{self.__host_mongo}:{self.__port_mongo}"
            if self.debug and self.FIRST_START:
                print(INFO["settings_db_url"].format(db_type=db_type, url=self.__mongo_url))
            return
        raise ApplicationException(f"Не реализована логика для подключения к базе данных <{db_type}>!")

    @property
    def get_postgres_url(self) -> str:
        """Ссылка для подключения к бд."""
        return self.__postgres_url

    @property
    def get_mongo_url(self) -> str:
        """
        Ссылка для подключения к бд.

        :example: "mongodb://user:pass@localhost:port"
        """
        return self.__mongo_url
