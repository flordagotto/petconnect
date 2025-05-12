from dataclasses import dataclass
from bounded_contexts.pets_domain.entities import PetSight, Pet
from bounded_contexts.pets_domain.services import PetService
from bounded_contexts.pets_domain.services.pet_sight_service import PetSightService
from bounded_contexts.pets_domain.views.pet_sight_view import (
    PetSightViewFactory,
    PetSightView,
)
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class RegisterPetSightUseCase(BaseUseCase):
    @dataclass
    class Request:
        pet_id: str
        latitude: float
        longitude: float
        account_id: str | None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_sight_service: PetSightService,
        pet_service: PetService,
        pet_sight_view_factory: PetSightViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.pet_sight_service = pet_sight_service
        self.pet_service = pet_service
        self.pet_sight_view_factory = pet_sight_view_factory

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> PetSightView:
        pet: Pet = await self.pet_service.get_pet_by_id(
            uow=uow, entity_id=request.pet_id
        )

        pet_sight: PetSight = await self.pet_sight_service.create_pet_sight(
            uow=uow,
            pet=pet,
            latitude=request.latitude,
            longitude=request.longitude,
            account_id=request.account_id,
        )

        return self.pet_sight_view_factory.create_pet_sight_view(pet_sight=pet_sight)
