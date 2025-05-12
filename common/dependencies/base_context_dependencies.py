from abc import ABC, abstractmethod
from common.dependencies import DependencyContainer


class BaseContextDependencies(ABC):
    def __init__(self, dependencies: DependencyContainer) -> None:
        self.dependencies = dependencies

    def initialize(self) -> None:
        self._initialize_view_factories()
        self._initialize_repositories()
        self._initialize_services()
        self._initialize_use_cases()
        self._initialize_event_handlers()

    @abstractmethod
    def _initialize_view_factories(self) -> None:
        pass

    @abstractmethod
    def _initialize_repositories(self) -> None:
        pass

    @abstractmethod
    def _initialize_services(self) -> None:
        pass

    @abstractmethod
    def _initialize_use_cases(self) -> None:
        pass

    @abstractmethod
    def _initialize_event_handlers(self) -> None:
        pass
