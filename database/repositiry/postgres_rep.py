import uuid
from abc import ABC, abstractmethod
from typing import Sequence, Type, Any

from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from typing_extensions import TypeVar

from database.dto.dto import Reminder, Base
from database.repositiry.base import BaseRepository
from exceptions.app import ValidationException

CLS = TypeVar("CLS", bound=Type[Base] | InstrumentedAttribute[str])


class BasePostgresRepository(BaseRepository, ABC):

    @abstractmethod
    async def get_by_filter(self, stmt: CLS, **stmt_filter_by) -> Sequence[CLS]:
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

    async def get_by_filter(self, stmt: CLS | InstrumentedAttribute[Any] = Reminder, **stmt_filter_by: object
                            ) -> Sequence[Reminder]:
        return await super().get_by_filter(stmt=stmt, **stmt_filter_by)

    # async def get_by_filter(self, stmt: CLS | None = None, **stmt_filter) -> Sequence[CLS]:
    #     """
    #     Исполнение запроса с фильтром к модели `Reminder`.
    #         Если присутствует `stmt` игнорируется `stmt_filter`.
    #
    #     :param stmt_filter: Аргумента для filter_by `Reminder`.
    #     :param stmt: Полное выражение для исполнения запроса.
    #     :return: Выдача запроса.
    #     """
    #     if stmt is None:
    #         if stmt_filter is not None:
    #             stmt = select(Reminder).filter_by(**stmt_filter)
    #     async with self.session(echo=False) as ses:  # type: AsyncSession
    #         results = await ses.execute(stmt)
    #         return results.scalars().all()  # type: ignore

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
