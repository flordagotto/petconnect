from abc import ABC
from typing import TypeVar, Type, Callable, Coroutine, Any
from awebus import Bus


class Event(ABC):
    EXTERNAL_ACTOR_ACCOUNT_ID = "<external>"

    """
        Abstract Event class that defines concrete Event class' interface.
    """

    def __init__(self, actor_account_id: str, issued: float) -> None:
        self.actor_account_id = actor_account_id
        self.issued = issued

    @classmethod
    def event_id(cls) -> str:
        return cls.__name__


class EventBus:
    EVENT_T = TypeVar("EVENT_T", bound=Event)

    def __init__(self) -> None:
        self.__bus_impl = Bus(event_use_weakref=False)

    def on(
        self,
        event_class: Type[EVENT_T],
        handler: Callable[[EVENT_T], Coroutine[Any, Any, None]],
    ) -> None:
        self.__bus_impl.on(event_class.event_id(), handler)

    async def post_events(self, events: list[Event]) -> None:
        for event in events:
            await self.__bus_impl.emitAsync(event.event_id(), event)  # type: ignore


app_event_bus = EventBus()
