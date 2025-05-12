from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator, Callable, Coroutine
from infrastructure.uow_abstraction import Event, EventBus, app_event_bus
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.ext.asyncio import async_sessionmaker


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self.__event_bus: EventBus = app_event_bus
        self.__events: list[Event] = list()
        self.__session = session
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def session(self) -> Session:
        if self._closed:
            raise Exception("SQLAlchemy Session is closed, access is forbidden")

        return self.__session

    async def flush(self) -> None:
        await self.__session.flush()

    async def commit(self) -> None:
        self._closed = True
        await self.__session.commit()
        await self.__publish_events()

    async def rollback(self, close_session: bool = True) -> None:
        if close_session:
            self._closed = True

        await self.__session.rollback()
        self.__events.clear()

    def emit_event(self, event: Event) -> None:
        self.__events.append(event)

    async def __publish_events(self) -> None:
        await self.__event_bus.post_events(self.__events)
        self.__events.clear()


@asynccontextmanager
async def make_unit_of_work(
    async_session_maker: async_sessionmaker,
) -> AsyncGenerator[UnitOfWork, None]:
    uow: UnitOfWork
    async with async_session_maker() as session:
        try:
            uow = UnitOfWork(session=session)

            # Force initial rollback to ensure hanging operations are killed
            await uow.rollback(close_session=False)

            async with session.begin():
                yield uow

            await uow.commit()

        except BaseException as be:
            await uow.rollback(close_session=True)
            raise be


def unit_of_work(async_fn: Callable[..., Coroutine]):
    @wraps(async_fn)
    async def new_coroutine(self, *args, **kwargs):
        if kwargs.get("uow"):
            return await async_fn(self, *args, **kwargs)

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            res = await async_fn(self, *args, **kwargs, uow=uow)

        return res

    return new_coroutine
