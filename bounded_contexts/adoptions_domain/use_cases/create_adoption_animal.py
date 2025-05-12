from dataclasses import dataclass
from datetime import date

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.use_cases.base_adoptions_use_case import (
    BaseAdoptionsUseCase,
)
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
    AdoptionAnimalView,
)
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from infrastructure.database import RepositoryUtils
from infrastructure.date_utils import date_now
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreateAdoptionAnimalUseCase(BaseAdoptionsUseCase):
    @dataclass
    class Request:
        animal_name: str
        birth_year: int
        species: AnimalSpecies
        gender: AnimalGender
        size: AnimalSize
        sterilized: bool
        vaccinated: bool
        account_id: str
        picture: str
        publication_date: date | None = date_now()
        race: str | None = None
        special_care: str | None = None
        description: str | None = None

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
                uow=uow, account_id=request.account_id
            )
        )

        adoption_animal: AdoptionAnimal = (
            await self.adoption_animal_service.create_adoption_animal(
                uow=uow,
                actor_profile=actor_profile,
                animal_name=request.animal_name,
                birth_year=request.birth_year,
                species=request.species,
                gender=request.gender,
                size=request.size,
                sterilized=request.sterilized,
                vaccinated=request.vaccinated,
                picture=request.picture,
                state=AdoptionAnimalStates.FOR_ADOPTION,
                race=request.race,
                special_care=request.special_care,
                description=request.description,
                publication_date=request.publication_date,
            )
        )

        return self.adoption_animal_view_factory.create_adoption_animal_view(
            adoption_animal=adoption_animal,
            publicator_name=actor_profile.first_name,
        )
