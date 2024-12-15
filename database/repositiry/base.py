from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Sequence

from sqlalchemy import Executable, Row
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import DataBasesSessionsManager
from database.dto.dto import Base, Reminder
from database.dto.dto_mongo import BaseNotification
from property.settings import Settings

CLS = TypeVar("CLS", bound=Base)
MCLS = TypeVar("MCLS", bound=BaseNotification)


@dataclass
class FullDBObjectNotification:
    postgres_notify: Reminder | None
    mongo_notify: MCLS | None


    def __str__(self):
        return "12"

class BaseRepository(ABC):
    settings = Settings()
    session = DataBasesSessionsManager.get_postgres_session

    @abstractmethod
    async def get_by_id(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create_objects(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete_objects(self, *args, **kwargs):
        pass

    async def do_session_execute(self, stmt: Executable) -> Sequence[Row[CLS]]:
        """
        Запрос для более низкоуровневых простых запросов.

        :param stmt: Выражение для исполнения.

        :return: Последовательность результатов поиска.
        """
        async with self.session(echo=self.settings.debug) as ses:  # type: AsyncSession
            results = await ses.execute(stmt)
            if not results:
                return []
            return results.fetchall()

    async def do_solo_session_execute(self, stmt: Executable) -> Sequence[CLS]:
        """
        Запрос для более простых запросов с одним ответом.

        :param stmt: Выражение для исполнения.

        :return: Последовательность моделей.
        """
        async with self.session(echo=self.settings.debug) as ses:  # type: AsyncSession
            results = await ses.execute(stmt)
            if not results:
                return []
            return results.scalars().all()
