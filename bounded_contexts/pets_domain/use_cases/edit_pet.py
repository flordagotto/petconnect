from dataclasses import dataclass
from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.services import PetService, ModifyPetData
from bounded_contexts.pets_domain.use_cases import BasePetsUseCase
from bounded_contexts.pets_domain.views import PetViewFactory, PetView
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


# Use cases that map to PUT and DELETE routes must follow idempotency:
# https://developer.mozilla.org/en-US/docs/Glossary/Idempotent
class EditPetUseCase(BasePetsUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        pet_data: ModifyPetData

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        pet_view_factory: PetViewFactory,
        profile_service: ProfileService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            pet_service=pet_service,
            pet_view_factory=pet_view_factory,
        )

        self.profile_service = profile_service
        self.pet_service = pet_service

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> PetView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.actor_account_id
            )
        )

        pet: Pet = await self.pet_service.get_pet_by_id(
            uow=uow,
            entity_id=request.pet_data.entity_id,
        )

        await self.pet_service.edit_pet(
            uow=uow,
            actor_profile=actor_profile,
            pet=pet,
            new_pet_data=request.pet_data,
        )

        updated_pet: Pet = await self.pet_service.get_pet_by_id(
            uow=uow,
            entity_id=request.pet_data.entity_id,
        )

        return self.pet_view_factory.create_pet_view(pet=updated_pet)
