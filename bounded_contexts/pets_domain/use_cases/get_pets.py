from dataclasses import dataclass
from typing import Sequence, Dict

from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.services import PetService
from bounded_contexts.pets_domain.use_cases import BasePetsUseCase
from bounded_contexts.pets_domain.views import PetViewFactory, PetListView
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetPetsUseCase(BasePetsUseCase):
    @dataclass
    class Request:
        limit: int | None
        offset: int | None
        lost: bool | None
        profile_id: str | None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        profile_service: ProfileService,
        pet_view_factory: PetViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            pet_service=pet_service,
            pet_view_factory=pet_view_factory,
        )

        self.profile_service = profile_service

    @unit_of_work
    async def execute(self, request: Request, uow: UnitOfWork) -> PetListView:
        pets: Sequence[Pet] = await self.pet_service.get_all_pets(
            uow=uow,
            limit=request.limit,
            offset=request.offset,
            lost=request.lost,
            profile_id=request.profile_id,
        )
        total_count: int = await self.pet_service.get_all_pets_count(
            uow=uow, lost=request.lost, profile_id=request.profile_id
        )

        pets_dict = await self.get_extra_info_for_pets(uow=uow, pets=pets)

        return self.pet_view_factory.create_pet_list_view(
            pets=pets_dict, total_count=total_count
        )

    async def get_extra_info_for_pets(
        self,
        uow: UnitOfWork,
        pets: Sequence[Pet],
    ) -> Dict[Pet, str]:
        pets_dict = {}
        for pet in pets:
            owner = await self.profile_service.get_profile(
                uow=uow, entity_id=pet.profile_id
            )
            pets_dict[pet] = owner.first_name + " " + owner.surname
        return pets_dict
