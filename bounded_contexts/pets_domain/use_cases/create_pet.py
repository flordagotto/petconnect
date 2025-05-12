from dataclasses import dataclass
from datetime import date

from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.services import PetService
from bounded_contexts.pets_domain.use_cases import BasePetsUseCase
from bounded_contexts.pets_domain.views import PetViewFactory, PetView
from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreatePetUseCase(BasePetsUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        animal_name: str
        birth_year: int
        species: AnimalSpecies
        gender: AnimalGender
        size: AnimalSize
        sterilized: bool
        vaccinated: bool
        lost: bool
        picture: str
        lost_date: date | None = None
        race: str | None = None
        special_care: str | None = None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        pet_view_factory: PetViewFactory,
        profile_service: ProfileService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            pet_service=pet_service,
            pet_view_factory=pet_view_factory,
        )

        self.profile_service = profile_service
        self.pet_service = pet_service

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> PetView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.actor_account_id
            )
        )

        pet: Pet = await self.pet_service.create_pet(
            uow=uow,
            actor_profile=actor_profile,
            animal_name=request.animal_name,
            birth_year=request.birth_year,
            species=request.species,
            gender=request.gender,
            size=request.size,
            sterilized=request.sterilized,
            vaccinated=request.vaccinated,
            lost=request.lost,
            lost_date=request.lost_date,
            race=request.race,
            special_care=request.special_care,
            picture=request.picture,
        )

        return self.pet_view_factory.create_pet_view(pet=pet)
