import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import DataBasesSessionsManager
from database.dto.dto import Reminder
from database.repositiry.base import BaseRepository


class ReminderRepository(BaseRepository):

    def __init__(self) -> None:
        self.session = DataBasesSessionsManager.get_postgres_session

    async def get_by_id(self, id_: int | uuid.UUID | str) -> Reminder | None:
        stmt = select(Reminder).where(Reminder.uuid == id_)
        async with self.session() as ses:  # type: AsyncSession
            results = await ses.execute(stmt)
            return results.scalar_one_or_none()

    async def get_by_filter(self, stmt: Any | None = None, **stmt_filter):
        """
        Исполнение запроса с фильтром к модели `Reminder`.
            Если присутствует `stmt` игнорируется `stmt_filter`.

        :param stmt_filter: Аргумента для filter_by `Reminder`.
        :param stmt: Полное выражение для исполнения запроса.
        :return: Выдача запроса.
        """
        if stmt is None:
            if stmt_filter is not None:
                stmt = select(Reminder).filter_by(**stmt_filter)

        async with self.session(echo=False) as ses:  # type: AsyncSession
            results = await ses.execute(stmt)
            return results.scalars().all()  # type: ignore

    async def create_objects(self, new_object):
        pass
