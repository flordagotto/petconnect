from dataclasses import dataclass
from typing import Sequence

from bounded_contexts.pets_domain.entities import PetSight
from bounded_contexts.pets_domain.services import PetSightService
from bounded_contexts.pets_domain.views import PetSightViewFactory
from bounded_contexts.pets_domain.views.pet_sight_view import PetSightListView
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetPetSightsUseCase(BaseUseCase):
    @dataclass
    class Request:
        limit: int | None
        offset: int | None
        pet_id: str | None = None
        lost: bool | None = None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_sight_service: PetSightService,
        pet_sight_view_factory: PetSightViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.pet_sight_service = pet_sight_service
        self.pet_sight_view_factory = pet_sight_view_factory

    @unit_of_work
    async def execute(self, request: Request, uow: UnitOfWork) -> PetSightListView:
        pet_sights: Sequence[
            PetSight
        ] = await self.pet_sight_service.get_all_pet_sights(
            uow=uow,
            limit=request.limit,
            offset=request.offset,
            pet_id=request.pet_id,
            lost=request.lost,
        )

        total_count: int = await self.pet_sight_service.get_all_pet_sights_count(
            uow=uow, pet_id=request.pet_id, lost=request.lost
        )

        return self.pet_sight_view_factory.create_pet_sight_list_view(
            pet_sights=pet_sights, total_count=total_count
        )
