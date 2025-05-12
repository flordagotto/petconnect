from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.events.adoption_events_handler import (
    AnimalAdoptedEvent,
)
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.pets_domain.email.pet_email_templates import (
    PetEmailSubjects,
    render_pet_sight_template,
)
from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.events import PetLostEvent, PetSightingEvent
from bounded_contexts.pets_domain.services import PetService, PetSightService
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from config import UrlConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import EventBus, make_unit_of_work


class PetEventHandler:
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        pet_sight_service: PetSightService,
        profile_service: ProfileService,
        adoption_animal_service: AdoptionAnimalsService,
        event_bus: EventBus,
        email_gateway: BaseEmailGateway,
        url_config: UrlConfig,
    ) -> None:
        self.repository_utils = repository_utils
        self.pet_service = pet_service
        self.pet_sight_service = pet_sight_service
        self.profile_service = profile_service
        self.adoption_animal_service = adoption_animal_service
        self.email_gateway = email_gateway
        self.url_config = url_config

        event_bus.on(PetLostEvent, self.__register_first_sight)
        event_bus.on(PetSightingEvent, self.__handle_pet_sight_event)
        event_bus.on(AnimalAdoptedEvent, self.__create_pet_from_adopted_animal)

    async def __register_first_sight(self, e: PetLostEvent) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet: Pet = await self.pet_service.get_pet_by_id(uow=uow, entity_id=e.pet_id)

            last_known_latitude = pet.last_known_latitude
            last_known_longitude = pet.last_known_longitude

            if last_known_latitude is None or last_known_longitude is None:
                return

            await self.pet_sight_service.create_pet_sight(
                uow=uow,
                account_id=e.actor_account_id,
                pet=pet,
                latitude=last_known_latitude,
                longitude=last_known_longitude,
            )

    async def __handle_pet_sight_event(self, e: PetSightingEvent) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet: Pet = await self.pet_service.get_pet_by_id(uow=uow, entity_id=e.pet_id)

            owner = await self.profile_service.get_profile(
                uow=uow, entity_id=pet.profile_id
            )

        await self.__send_pet_sight_email(
            email=owner.account.email,
            profile_name=owner.first_name,
            pet_id=e.pet_id,
            fe_route="lost-pets",
        )

    async def __send_pet_sight_email(
        self, email: str, profile_name: str, pet_id: str, fe_route: str
    ) -> None:
        self.email_gateway.schedule_mail(
            recipient=email,
            subject=PetEmailSubjects.PET_SIGHT.value,
            body=render_pet_sight_template(
                profile_name=profile_name,
                lost_pets_url=f"{self.url_config.frontend_url}"
                f"/{fe_route}?petId={pet_id}",
            ),
        )

    async def __create_pet_from_adopted_animal(self, e: AnimalAdoptedEvent) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adopter_profile: BaseProfile = (
                await self.profile_service.get_profile_by_account_id(
                    uow=uow, account_id=e.actor_account_id
                )
            )

            animal: AdoptionAnimal = (
                await self.adoption_animal_service.get_adoption_animal_by_id(
                    uow=uow, entity_id=e.animal_id
                )
            )

            await self.pet_service.create_pet(
                uow=uow,
                animal_name=animal.animal_name,
                birth_year=animal.birth_year,
                species=animal.species,
                gender=animal.gender,
                size=animal.size,
                sterilized=animal.sterilized,
                vaccinated=animal.vaccinated,
                picture=animal.picture,
                lost=False,
                race=animal.race,
                special_care=animal.special_care,
                actor_profile=adopter_profile,
                adoption_animal_id=animal.entity_id,
            )
