from abc import abstractmethod
from common.dependencies import DependencyContainer
from infrastructure.rest import BaseAPIController


class RouteManager:
    def __init__(self, dependencies: DependencyContainer) -> None:
        self.dependencies: DependencyContainer = dependencies

    def register_routes(self) -> None:
        routes: list[BaseAPIController] = self._create_controllers()

        for route in routes:
            route.register_routes()

    @abstractmethod
    def _create_controllers(self) -> list[BaseAPIController]:
        pass
