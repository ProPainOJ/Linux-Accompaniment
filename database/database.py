from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from exceptions.database import ConfigException
from property.settings import DataBaseSettings


class DataBasesSessionsManager:
    """Контекстный менеджер для реализации запрос к бд."""

    @staticmethod
    @asynccontextmanager
    async def get_postgres_session(expire: bool | None = False, echo: bool | None = DataBaseSettings().echo,
                                   url: str | None = DataBaseSettings().get_postgres_url) -> AsyncGenerator[
        AsyncSession]:
        engine = create_async_engine(url=url, echo=echo)
        _async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=expire)
        try:
            async with _async_session() as session:
                yield session
        except Exception as e:
            await session.rollback()
            print(f"\n\t>>> ERROR: {e}.\n")
        finally:
            await session.close()

    @staticmethod
    def get_mongo_db_motor(
            url: str = DataBaseSettings().get_mongo_url, db_name: str | None = "LA",
            collection_name: str | None = "Notifications"
    ) -> AsyncIOMotorDatabase | AsyncIOMotorCollection | AsyncIOMotorClient | ConfigException:
        """
        Получение `мотора` mongodb.
            :EXTRA INFO:
            Передача (db_name, collection_name) = None вернёт AsyncIOMotorClient.
        :param db_name: Название базы данных.
        :param collection_name: Название коллекции.
        :param url: Ссылка для подключения к бд.

        :return: Client(motor)/Database/Collection
        """
        if collection_name is None and db_name is None:
            return AsyncIOMotorClient(url)
        if db_name:
            db: AsyncIOMotorDatabase = AsyncIOMotorClient(url).get_database(name=db_name)
            if collection_name:
                return db.get_collection(name=collection_name)
            return db
        else:
            raise ConfigException(f"Не передано название бд для поиска коллекции <{collection_name}>!")
