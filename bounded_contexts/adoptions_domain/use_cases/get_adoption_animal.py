from typing import cast

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.use_cases.base_adoptions_use_case import (
    BaseAdoptionsUseCase,
)
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
    AdoptionAnimalView,
)
from bounded_contexts.social_domain.entities import BaseProfile, OrganizationalProfile
from bounded_contexts.social_domain.enum import ProfileTypes
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetAdoptionAnimalUseCase(BaseAdoptionsUseCase):
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
        self,
        entity_id: str,
        uow: UnitOfWork,
    ) -> AdoptionAnimalView:
        adoption_animal: AdoptionAnimal = (
            await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow, entity_id=entity_id
            )
        )

        profile: BaseProfile = await self.profile_service.get_profile(
            uow=uow, entity_id=adoption_animal.profile_id
        )

        publicator_name: str

        if profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
            organizational_profile: OrganizationalProfile = cast(
                OrganizationalProfile, profile
            )

            organization = await self.organization_service.get_organization_by_id(
                uow=uow, entity_id=organizational_profile.organization_id
            )

            publicator_name = organization.organization_name

        else:
            publicator_name = profile.first_name

        return self.adoption_animal_view_factory.create_adoption_animal_view(
            adoption_animal=adoption_animal,
            publicator_name=publicator_name,
        )
