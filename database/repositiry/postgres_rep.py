import uuid

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
        async with self.session() as ses:
            results = await ses.execute(stmt)
            return results.scalar_one_or_none()

    async def create_objects(self, new_object):
        pass
