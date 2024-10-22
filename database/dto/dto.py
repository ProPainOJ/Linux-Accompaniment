from typing import Optional

from sqlalchemy import text, Date, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return self._my_repr()

    def _my_repr(self, field: Optional[dict[str, str | list[str]]] = None) -> str:
        repr_fields = [f">>> {self.__class__.__name__}({self.__tablename__}): "]
        if field is None:
            field = self.__dict__
            field.pop("_sa_instance_state")

        if not field:
            repr_fields.append(f"<{id(self)}>")

        for key, val in field.items():
            val = str(val) if not isinstance(val, list) else f"[{" | ".join(val)}]"
            repr_fields.append(f"{key}={val}")

        return repr_fields[0] + ", ".join(repr_fields[1:])


class Reminder(Base):
    __tablename__ = "reminder"

    uuid: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    create_data = mapped_column(Date, comment="Дата создания уведомления.")
    target_data = mapped_column(Date, comment="Дата исполнения уведомления.")
    target_time = mapped_column(Time, comment="Время исполнения уведомления.")
    status: Mapped[bool] = mapped_column(comment="Статус выполнения.")
    mongo_uuid: Mapped[str] = mapped_column(comment="Ссылка на тело уведомления.")
    urgency_id: Mapped[int] = mapped_column(comment="ID уровня важности уведомления.")
    repeat_id: Mapped[int] = mapped_column(comment="ID повторения уведомления.")

    def __repr__(self):
        return super()._my_repr({
            "uuid": self.uuid,
            "mongo_uuid": self.mongo_uuid,
            "target <time|data>": [
                self.target_time.strftime("%H:%M:%S"),
                self.target_data.strftime("%Y-%m-%d"),
            ]
        })
