import uuid
from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id_: int | uuid.UUID | str):
        pass

    @abstractmethod
    async def create_objects(self, new_object):
        pass
