from dataclasses import dataclass

from bounded_contexts.adoptions_domain.entities import (
    AdoptionApplication,
    AdoptionAnimal,
)
from bounded_contexts.adoptions_domain.enum import (
    HousingTypes,
    OpenSpacesTypes,
)
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    AdoptionApplicationService,
)
from bounded_contexts.adoptions_domain.views.adoption_application_views import (
    AdoptionApplicationViewFactory,
    AdoptionApplicationView,
)
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.views import ProfileViewFactory
from bounded_contexts.social_domain.views.profile_views import BaseProfileView
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreateAdoptionApplicationUseCase(BaseUseCase):
    @dataclass
    class Request:
        ever_had_pet: bool
        has_pet: bool
        type_of_housing: HousingTypes
        open_space: OpenSpacesTypes
        pet_time_commitment: str
        adoption_info: str
        adopter_account_id: str
        animal_id: str
        safety_in_open_spaces: str | None = None
        animal_nice_to_others: str | None = None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_application_service: AdoptionApplicationService,
        adoption_application_view_factory: AdoptionApplicationViewFactory,
        profile_view_factory: ProfileViewFactory,
        profile_service: ProfileService,
        animal_service: AdoptionAnimalsService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.adoption_application_service = adoption_application_service
        self.adoption_application_view_factory = adoption_application_view_factory
        self.profile_view_factory = profile_view_factory
        self.profile_service = profile_service
        self.animal_service = animal_service

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> AdoptionApplicationView:
        adopter_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.adopter_account_id
            )
        )

        animal: AdoptionAnimal = await self.animal_service.get_adoption_animal_by_id(
            uow=uow, entity_id=request.animal_id
        )

        application: AdoptionApplication = (
            await self.adoption_application_service.create_application(
                uow=uow,
                adopter_profile=adopter_profile,
                ever_had_pet=request.ever_had_pet,
                has_pet=request.has_pet,
                type_of_housing=request.type_of_housing,
                open_space=request.open_space,
                pet_time_commitment=request.pet_time_commitment,
                adoption_info=request.adoption_info,
                animal=animal,
                safety_in_open_spaces=request.safety_in_open_spaces,
                animal_nice_to_others=request.animal_nice_to_others,
            )
        )

        profile_view: BaseProfileView = self.profile_view_factory.create_profile_view(
            adopter_profile
        )

        return self.adoption_application_view_factory.create_adoption_application_view(
            application=application,
            profile_view=profile_view,
            animal_name=animal.animal_name,
        )
