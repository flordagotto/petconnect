import logging
from abc import abstractmethod, ABC
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import close_all_sessions, registry
from config import DatabaseConfig
from infrastructure.uow_abstraction.unit_of_work_module import make_unit_of_work
from .manage_tables import create_tables


class DatabaseUrlProvider(ABC):
    @abstractmethod
    def connection_url(self) -> str:
        pass

    @abstractmethod
    def describe_connection_for_logging(self) -> str:
        pass


class PostgresUrlProvider(DatabaseUrlProvider):
    def __init__(self, db_config: DatabaseConfig) -> None:
        self.protocol = "postgresql+asyncpg"
        self.user = db_config.connection.user
        self.password = db_config.connection.password
        self.host = db_config.connection.host
        self.db_name = db_config.connection.db_name
        self.port = db_config.connection.port

    def connection_url(self) -> str:
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}/{self.db_name}?port={self.port}"

    def describe_connection_for_logging(self) -> str:
        return f"{self.protocol}://{self.host}/{self.db_name}?port={self.port}"


def get_url_provider(db_config: DatabaseConfig) -> DatabaseUrlProvider:
    providers = {
        "postgresql": PostgresUrlProvider,
    }

    return providers[db_config.db](db_config)


class RepositoryUtils:
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self,
        db_config: DatabaseConfig,
    ) -> None:
        self.db_config = db_config

        url_provider: DatabaseUrlProvider = get_url_provider(db_config=self.db_config)

        connection_url: str = url_provider.connection_url()
        should_echo: bool = self.db_config.echo

        self.logger.info(
            f"Connecting database '{url_provider.describe_connection_for_logging()}'"
        )
        self.logger.info(f"Database pool configuration: {self.db_config.pool}")

        self.engine = create_async_engine(
            future=True,
            url=connection_url,
            echo=should_echo,
            max_overflow=int(self.db_config.pool.max_overflow),
            pool_recycle=int(self.db_config.pool.recycle),
            pool_size=int(self.db_config.pool.size),
            pool_timeout=int(self.db_config.pool.timeout),
            connect_args={"server_settings": {"jit": "off"}},
        )

        self.metadata = MetaData()
        self.orm_registry = registry()
        self.sessionmaker = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
        )

    async def create_metadata(self) -> None:
        await create_tables(
            metadata=self.metadata,
            orm_registry=self.orm_registry,
            db_engine=self.engine,
        )

    async def clear_database(self) -> None:
        try:
            close_all_sessions()
        except Exception as e:
            self.logger.error("Error closing sessions", exc_info=e)

        async with make_unit_of_work(self.sessionmaker) as uow:
            for table in reversed(self.metadata.sorted_tables):
                await uow.session.execute(table.delete())

    async def dispose_engine(self) -> None:
        await self.engine.dispose()

    @staticmethod
    def close_all_sessions() -> None:
        close_all_sessions()
