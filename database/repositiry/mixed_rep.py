import uuid

from bson import ObjectId
from sqlalchemy.orm import InstrumentedAttribute

from database.repositiry.base import BaseRepository, FullDBObjectNotification
from database.repositiry.mongo_rep import NotificationsRepository
from database.repositiry.postgres_rep import ReminderRepository


class MixedRepository(BaseRepository):
    def __init__(self):
        self.postgres_rep = ReminderRepository()
        self.mongo_rep = NotificationsRepository()
        self._full_notification = FullDBObjectNotification
        self._res_full_notification: list[FullDBObjectNotification] = []

    async def get_by_id(self, id_: int | uuid.UUID | str):
        pass

    async def create_objects(self, new_object):
        pass

    async def delete_objects(self, obj_to_delete: FullDBObjectNotification) -> None:
        ses = await self.postgres_rep.delete_objects(delete_obj=[obj_to_delete.postgres_notify.uuid])
        motor_client = self.mongo_rep
        async with motor_client.motor.start_session():
            del_result = await motor_client.delete_objects([obj_to_delete.mongo_notify.to_dict()["_id"]])
        if del_result:
            await ses.commit()

    async def get_by_filters(self, filters: dict[InstrumentedAttribute[str], str]) -> list[FullDBObjectNotification]:
        """

        :param filters:
        :return:
        """
        postgres_notification = {
            ObjectId(rem.mongo_uuid): rem
            for rem in await self.postgres_rep.get_by_filter(filters)
        }

        mongo_bodies = await self.mongo_rep.get_by_filter({
            "_id": {"$in": list(postgres_notification.keys())}
        })

        for mongo_body in mongo_bodies:
            self._res_full_notification.append(
                self._full_notification(
                    postgres_notify=postgres_notification[mongo_body.notify["_id"]],
                    mongo_notify=mongo_body,
                ),
            )

        return self._res_full_notification
