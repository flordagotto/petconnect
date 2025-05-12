from dataclasses import dataclass

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class DeleteAdoptionAnimalUseCase(BaseUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        entity_id: str

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_animal_service: AdoptionAnimalsService,
        profile_service: ProfileService,
    ) -> None:
        super().__init__(repository_utils=repository_utils)
        self.adoption_animal_service = adoption_animal_service
        self.profile_service = profile_service

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
        adoption_animal: AdoptionAnimal = (
            await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow,
                entity_id=request.entity_id,
            )
        )

        await self.adoption_animal_service.delete_adoption_animal(
            uow=uow, actor_profile=actor_profile, adoption_animal=adoption_animal
        )
