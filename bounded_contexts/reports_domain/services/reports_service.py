from typing import Sequence

from bounded_contexts.reports_domain.dataclasses import AdoptedAnimal, CollectedMoney
from bounded_contexts.reports_domain.dataclasses.lost_and_found_pets import (
    LostAndFoundPets,
)
from bounded_contexts.reports_domain.repositories import ReportsRepository
from infrastructure.uow_abstraction import UnitOfWork


class ReportService:
    def __init__(
        self,
        reports_repository: ReportsRepository,
    ) -> None:
        self.reports_repository = reports_repository

    async def get_adopted_animals(
        self, uow: UnitOfWork, organization_id: str | None = None
    ) -> Sequence[AdoptedAnimal]:
        return await self.reports_repository.get_adopted_animals(
            session=uow.session, organization_id=organization_id
        )

    async def get_collected_money(
        self, uow: UnitOfWork, organization_id: str | None
    ) -> Sequence[CollectedMoney]:
        return await self.reports_repository.get_collected_money(
            session=uow.session,
            organization_id=organization_id,
        )

    async def get_lost_and_found_pets(
        self, uow: UnitOfWork
    ) -> Sequence[LostAndFoundPets]:
        return await self.reports_repository.get_lost_and_found_pets(
            session=uow.session
        )
