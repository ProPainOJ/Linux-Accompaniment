import uuid
from abc import ABC, abstractmethod
from typing import Sequence, Type, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from typing_extensions import TypeVar

from database.dto.dto import Reminder, Base
from database.repositiry.base import BaseRepository
from exceptions.app import ValidationException

BASE_CLS = TypeVar("BASE_CLS", bound=Type[Base])
CLS = TypeVar("CLS", bound=Type[Base] | InstrumentedAttribute[str])


class BasePostgresRepository(BaseRepository, ABC):

    @abstractmethod
    async def get_by_filter_by(self, stmt: CLS, **stmt_filter_by) -> Sequence[CLS]:
        stmt = select(stmt)
        if stmt_filter_by is not None:
            stmt = stmt.filter_by(**stmt_filter_by)
        return await self.do_solo_session_execute(stmt)


class ReminderRepository(BasePostgresRepository):

    async def get_by_id(self, id_: int | uuid.UUID | str) -> Reminder | None:
        stmt = select(Reminder).where(Reminder.uuid == id_)
        async with self.session() as ses:  # type: AsyncSession
            results = await ses.execute(stmt)
            return results.scalar_one_or_none()

    async def get_by_filter_by(
            self, stmt: BASE_CLS = Reminder, **stmt_filter_by
    ) -> Sequence[BASE_CLS]:
        return await super().get_by_filter_by(stmt=stmt, **stmt_filter_by)

    async def get_by_filter(
            self,
            stmt_filter: dict[InstrumentedAttribute[str], str] = None,
            stmt: CLS | InstrumentedAttribute[Any] = Reminder,
    ) -> Sequence[CLS]:
        if stmt_filter:
            stmt_filter = (key.ilike(f"%{value}%") for key, value in stmt_filter.items())
            stmt = select(stmt).filter(*stmt_filter)
        else:
            stmt = select(stmt)
        return await self.do_solo_session_execute(stmt=stmt)

    async def create_objects(self, new_object: list[Reminder]):
        async with self.session() as ses:  # type: AsyncSession
            ses.add_all(new_object)
            await ses.commit()

    async def delete_objects(self, delete_obj: list[Reminder.uuid], return_ses: bool = False) -> bool | AsyncSession:
        async with self.session() as ses:  # type: AsyncSession
            if all((isinstance(rem, uuid.UUID) for rem in delete_obj)):
                stmt = select(Reminder).where(Reminder.uuid.in_(delete_obj))
                results = await self.do_solo_session_execute(stmt)
            else:
                raise ValidationException("Передан неверный аргумент `delete_obj`!")

            if results:
                for res in results:
                    await ses.delete(res)
                if not return_ses:
                    await ses.commit()
                else:
                    return ses

            return True if results else False
