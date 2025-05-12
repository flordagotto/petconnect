from dataclasses import dataclass
from typing import Sequence

from bounded_contexts.pets_domain.entities import Pet, PetSight
from bounded_contexts.pets_domain.services import PetService, PetSightService
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class DeletePetUseCase(BaseUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        entity_id: str

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        profile_service: ProfileService,
        pet_sight_service: PetSightService,
    ) -> None:
        super().__init__(repository_utils=repository_utils)
        self.pet_service = pet_service
        self.profile_service = profile_service
        self.pet_sight_service = pet_sight_service

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> None:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.actor_account_id
            )
        )
        pet: Pet = await self.pet_service.get_pet_by_id(
            uow=uow,
            entity_id=request.entity_id,
        )

        self.pet_service.validate_user_can_delete_pet(
            actor_profile=actor_profile, pet=pet
        )

        pet_sights: Sequence[
            PetSight
        ] = await self.pet_sight_service.get_all_pet_sights(
            uow=uow, pet_id=pet.entity_id
        )

        await self.pet_sight_service.delete_pet_sights(uow=uow, pet_sights=pet_sights)

        await self.pet_service.delete_pet(uow=uow, pet=pet)
