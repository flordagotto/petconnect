from typing import Sequence
from bounded_contexts.reports_domain.dataclasses.lost_and_found_pets import (
    LostAndFoundPets,
)
from bounded_contexts.reports_domain.services import ReportService
from bounded_contexts.reports_domain.use_cases.base_reports_use_case import (
    BaseReportsUseCase,
)
from bounded_contexts.reports_domain.views.lost_and_found_pets_view import (
    LostAndFoundPetsViewFactory,
    LostAndFoundPetsListView,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetLostAndFoundPetsUseCase(BaseReportsUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        reports_service: ReportService,
        lost_and_found_pets_view_factory: LostAndFoundPetsViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils, report_service=reports_service
        )
        self.lost_and_found_pets_view_factory = lost_and_found_pets_view_factory

    @unit_of_work
    async def execute(self, uow: UnitOfWork) -> LostAndFoundPetsListView:
        lost_and_found_pets: Sequence[LostAndFoundPets]

        lost_and_found_pets = await self.report_service.get_lost_and_found_pets(uow=uow)

        return (
            self.lost_and_found_pets_view_factory.create_lost_and_found_pets_list_view(
                lost_and_found_pets=lost_and_found_pets,
                total_count=len(lost_and_found_pets),
            )
        )
