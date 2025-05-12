from dataclasses import dataclass

from bounded_contexts.adoptions_domain.entities import (
    AdoptionAnimal,
    AdoptionApplication,
)
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    AdoptionApplicationService,
    ModifyAdoptionApplicationData,
)
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalsService,
)
from bounded_contexts.adoptions_domain.views.adoption_application_views import (
    AdoptionApplicationViewFactory,
    AdoptionApplicationView,
)
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class EditAdoptionApplicationUseCase(BaseUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        application_data: ModifyAdoptionApplicationData

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_application_view_factory: AdoptionApplicationViewFactory,
        adoption_application_service: AdoptionApplicationService,
        adoption_animal_service: AdoptionAnimalsService,
        profile_service: ProfileService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.adoption_application_service = adoption_application_service
        self.adoption_application_view_factory = adoption_application_view_factory
        self.adoption_animal_service = adoption_animal_service
        self.profile_service = profile_service

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> AdoptionApplicationView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.actor_account_id
            )
        )

        application: AdoptionApplication = (
            await self.adoption_application_service.get_application_by_id(
                uow=uow, entity_id=request.application_data.entity_id
            )
        )

        animal: AdoptionAnimal = (
            await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow,
                entity_id=application.animal_id,
            )
        )

        adopter_profile: BaseProfile = await self.profile_service.get_profile(
            uow=uow, entity_id=application.adopter_profile_id
        )

        await self.adoption_application_service.edit_application(
            uow=uow,
            actor_profile=actor_profile,
            animal=animal,
            application=application,
            application_new_data=request.application_data,
            adopter_profile=adopter_profile,
        )

        return self.adoption_application_view_factory.create_adoption_application_view(
            application=application, animal_name=animal.animal_name
        )

    # TODO: we should save a datetime when changing the state of the application
