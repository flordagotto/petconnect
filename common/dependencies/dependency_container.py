from typing import TypeVar, Type

T = TypeVar("T")


class DependencyContainer:
    def __init__(self) -> None:
        self._dependencies: dict = {}

    def register(self, class_type: Type[T], dependency: T) -> None:
        self._dependencies[class_type] = dependency

    def resolve(self, class_type: Type[T]) -> T:
        return self._dependencies[class_type]
