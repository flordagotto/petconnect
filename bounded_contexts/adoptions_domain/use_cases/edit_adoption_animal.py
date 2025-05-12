from dataclasses import dataclass

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    ModifyAdoptionAnimalData,
    AdoptionAnimalsService,
)
from bounded_contexts.adoptions_domain.use_cases.base_adoptions_use_case import (
    BaseAdoptionsUseCase,
)
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
    AdoptionAnimalView,
)
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class EditAdoptionAnimalUseCase(BaseAdoptionsUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        animal_data: ModifyAdoptionAnimalData

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_animal_service: AdoptionAnimalsService,
        adoption_animal_view_factory: AdoptionAnimalViewFactory,
        profile_service: ProfileService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            adoption_animal_service=adoption_animal_service,
            adoption_animal_view_factory=adoption_animal_view_factory,
        )

        self.profile_service = profile_service

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> AdoptionAnimalView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.actor_account_id
            )
        )

        animal: AdoptionAnimal = (
            await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow,
                entity_id=request.animal_data.entity_id,
            )
        )

        await self.adoption_animal_service.edit_adoption_animal(
            uow=uow,
            actor_profile=actor_profile,
            adoption_animal=animal,
            new_adoption_animal_data=request.animal_data,
        )

        return self.adoption_animal_view_factory.create_adoption_animal_view(
            adoption_animal=animal,
            publicator_name=actor_profile.first_name,
        )
