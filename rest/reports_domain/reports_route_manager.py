from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.reports_domain.reports import ReportsController


class ReportsRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        reports_controller: ReportsController = ReportsController(
            dependencies=self.dependencies,
        )

        return [reports_controller]
