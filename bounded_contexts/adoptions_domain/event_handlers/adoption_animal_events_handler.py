from typing import Sequence

from bounded_contexts.adoptions_domain.entities import AdoptionApplication
from bounded_contexts.adoptions_domain.events import AdoptionAnimalDeletedEvent
from bounded_contexts.adoptions_domain.services import (
    AdoptionAnimalsService,
    AdoptionApplicationService,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import EventBus, make_unit_of_work


class AdoptionAnimalEventHandler:
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_animal_service: AdoptionAnimalsService,
        adoption_application_service: AdoptionApplicationService,
        event_bus: EventBus,
    ) -> None:
        self.repository_utils = repository_utils
        self.adoption_animal_service = adoption_animal_service
        self.adoption_application_service = adoption_application_service

        event_bus.on(
            AdoptionAnimalDeletedEvent,
            self.__reject_applications_for_deleted_adoption_animal,
        )

    async def __reject_applications_for_deleted_adoption_animal(
        self, e: AdoptionAnimalDeletedEvent
    ) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adoption_applications: Sequence[
                AdoptionApplication
            ] = await self.adoption_application_service.get_applications_by_animal_id(
                uow=uow, adoption_animal_id=e.adoption_animal_id
            )

            await self.adoption_application_service.reject_applications(
                adoption_applications
            )
