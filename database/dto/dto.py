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
        repr_fields = [f"{self.__class__.__name__}({self.__tablename__}): "]
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
    _time_format: str = "%H:%M:%S"
    _data_format: str = "%Y-%m-%d"

    uuid: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(comment="Имя уведомления.", nullable=False)
    create_data = mapped_column(Date, comment="Дата создания уведомления.")
    target_data = mapped_column(Date, comment="Дата исполнения уведомления.", nullable=False)
    target_time = mapped_column(Time, comment="Время исполнения уведомления.", nullable=False)
    status: Mapped[bool] = mapped_column(comment="Статус выполнения.", default=False)
    mongo_uuid: Mapped[str] = mapped_column(comment="Ссылка на тело уведомления.", nullable=False)
    urgency_id: Mapped[int] = mapped_column(comment="ID уровня важности уведомления.", nullable=False, default=1)
    repeat_id: Mapped[int] = mapped_column(comment="ID повторения уведомления.")
    category_id: Mapped[int] = mapped_column(comment="ID категории уведомления.", default=1)

    def __repr__(self):
        return super()._my_repr({
            "uuid": self.uuid,
            "mongo_uuid": self.mongo_uuid,
            "target <time|data>": [
                self.target_time.strftime(self._time_format),
                self.target_data.strftime(self._data_format),
            ]
        })


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, comment="ID категории уведомлений."
                                    )
    name: Mapped[str] = mapped_column(comment="Название категории.")
    description: Mapped[str] = mapped_column(comment="Подробное описание повторений.")
    create_date = mapped_column(Date, comment="Дата создания категории повторений.")
