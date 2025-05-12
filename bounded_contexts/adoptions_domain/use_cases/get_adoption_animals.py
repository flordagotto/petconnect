from dataclasses import dataclass
from typing import Sequence, cast

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.use_cases.base_adoptions_use_case import (
    BaseAdoptionsUseCase,
)
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
    AdoptionAnimalListView,
)
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    BaseProfile,
    OrganizationalProfile,
    Organization,
)
from bounded_contexts.social_domain.enum import ProfileTypes
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetAdoptionAnimalsUseCase(BaseAdoptionsUseCase):
    @dataclass
    class Request:
        species: list[AnimalSpecies] | None
        limit: int | None
        offset: int | None
        account_id: str | None = None
        state: AdoptionAnimalStates | None = None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_animal_service: AdoptionAnimalsService,
        adoption_animal_view_factory: AdoptionAnimalViewFactory,
        profile_service: ProfileService,
        organization_service: OrganizationService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            adoption_animal_service=adoption_animal_service,
            adoption_animal_view_factory=adoption_animal_view_factory,
        )
        self.profile_service = profile_service
        self.organization_service = organization_service

    @unit_of_work
    async def execute(
        self, request: Request, uow: UnitOfWork
    ) -> AdoptionAnimalListView:
        actor_profile: BaseProfile | None = None

        if request.account_id:
            actor_profile = await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.account_id
            )

        animals = await self.adoption_animal_service.get_all_adoption_animals(
            uow=uow,
            species=request.species,
            limit=request.limit,
            offset=request.offset,
            profile=actor_profile,
            state=request.state,
        )

        total_count = await self.adoption_animal_service.get_all_adoption_animals_count(
            uow=uow,
            species=request.species,
            profile=actor_profile,
            state=request.state,
        )

        return self.adoption_animal_view_factory.create_adoption_animal_list_view(
            animals=animals,
            total_count=total_count,
            publicator_names=await self.get_publicator_names(
                uow=uow,
                animals=animals,
            ),
        )

    async def get_publicator_names(
        self, uow: UnitOfWork, animals: Sequence[AdoptionAnimal]
    ) -> dict[str, str]:
        # TODO: could be cleaner

        profile_ids: list[str] = [animal.profile_id for animal in animals]

        personal_profiles = (
            await self.profile_service.get_multiple_personal_profiles_by_id(
                uow=uow, profile_ids=profile_ids
            )
        )

        organizational_profiles = (
            await self.profile_service.get_multiple_organizational_profiles_by_id(
                uow=uow, profile_ids=profile_ids
            )
        )

        organizations: Sequence[
            Organization
        ] = await self.organization_service.get_multiple_organizations_by_id(
            uow=uow,
            organization_ids=[
                profile.organization_id for profile in organizational_profiles
            ],
        )

        organization_names: dict[str, str] = {
            organization.entity_id: organization.organization_name
            for organization in organizations
        }

        return {
            profile.entity_id: profile.first_name
            if profile.profile_type == ProfileTypes.PERSONAL_PROFILE
            else organization_names[
                cast(OrganizationalProfile, profile).organization_id
            ]
            for profile in [*personal_profiles, *organizational_profiles]
        }
