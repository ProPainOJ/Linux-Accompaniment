from bson import ObjectId
from pymongo.results import DeleteResult

from database.database import DataBasesSessionsManager
from database.dto.dto_mongo import GetNotification, CreateNotification, MongoTypes
from database.repositiry.base import BaseRepository


class NotificationsRepository(BaseRepository):
    def __init__(self) -> None:
        self.motor = DataBasesSessionsManager.get_mongo_db_motor()

    async def get_by_filter(self, filters: GetNotification | dict[str, MongoTypes] | None = None,
                            fields: dict[str, bool] = None, length: None | int = None) -> list[dict]:
        if fields is None:
            fields = {}
        if filters is None:
            filters = {}
        if isinstance(filters, GetNotification):
            filters = filters.to_dict()
        return await self.motor.find(filters, fields).to_list(length=length)

    async def get_by_id(self, _id: ObjectId) -> dict:
        return await self.motor.find_one({"_id": _id})

    async def create_objects(self, new_objects: list[CreateNotification]):
        return await self.motor.insert_many([new_object.__dict__() for new_object in new_objects])

    async def delete_objects_by_ids(self, del_object_list: list[ObjectId]) -> DeleteResult:
        return await self.motor.delete_many({"_id": {"$in": del_object_list}})
