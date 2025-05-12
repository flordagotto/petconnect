from dataclasses import dataclass
from typing import Sequence
from bounded_contexts.reports_domain.dataclasses import AdoptedAnimal
from bounded_contexts.reports_domain.services import ReportService
from bounded_contexts.reports_domain.use_cases.base_reports_use_case import (
    BaseReportsUseCase,
)
from bounded_contexts.reports_domain.views.adopted_animals_view import (
    AdoptedAnimalsListView,
    AdoptedAnimalsViewFactory,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetAdoptedAnimalsUseCase(BaseReportsUseCase):
    @dataclass
    class Request:
        organization_id: str | None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        reports_service: ReportService,
        adopted_animals_view_factory: AdoptedAnimalsViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils, report_service=reports_service
        )
        self.adopted_animals_view_factory = adopted_animals_view_factory

    @unit_of_work
    async def execute(
        self, request: Request, uow: UnitOfWork
    ) -> AdoptedAnimalsListView:
        animals: Sequence[AdoptedAnimal]

        animals = await self.report_service.get_adopted_animals(
            uow=uow, organization_id=request.organization_id
        )

        return self.adopted_animals_view_factory.create_adopted_animal_list_view(
            animals=animals,
            total_count=len(animals),
        )
