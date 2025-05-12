from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.files import FilesController


class FilesRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        files_controller: FilesController = FilesController(
            dependencies=self.dependencies,
        )

        return [files_controller]
