from dataclasses import dataclass
from datetime import date
from typing import Sequence, cast
from uuid import uuid4

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.events import AdoptionAnimalDeletedEvent
from bounded_contexts.adoptions_domain.exceptions import (
    AnimalNotFoundByIdException,
)
from bounded_contexts.adoptions_domain.exceptions.adoption_animal_unauthorized_access_exception import (
    AdoptionAnimalUnauthorizedAccessException,
)
from bounded_contexts.adoptions_domain.repositories import (
    AdoptionAnimalsRepository,
)
from bounded_contexts.auth.entities import Account
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
    BaseProfile,
    OrganizationalProfile,
)
from bounded_contexts.social_domain.enum import ProfileTypes
from infrastructure.date_utils import date_now, float_timestamp
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class AdoptionAnimalData:
    entity_id: str
    animal_name: str
    birth_year: int
    species: AnimalSpecies
    gender: AnimalGender
    size: AnimalSize
    sterilized: bool
    vaccinated: bool
    picture: str
    state: AdoptionAnimalStates
    deleted: bool = False
    publication_date: date | None = date_now()
    description: str | None = None
    special_care: str | None = None
    race: str | None = None


@dataclass
class ModifyAdoptionAnimalData:
    entity_id: str
    animal_name: str
    birth_year: int
    species: AnimalSpecies
    gender: AnimalGender
    size: AnimalSize
    sterilized: bool
    vaccinated: bool
    picture: str
    state: AdoptionAnimalStates
    description: str | None = None
    special_care: str | None = None
    race: str | None = None


class AdoptionAnimalsService:
    def __init__(
        self,
        animals_repository: AdoptionAnimalsRepository,
    ) -> None:
        self.animals_repository = animals_repository

    async def create_adoption_animal(
        self,
        uow: UnitOfWork,
        actor_profile: BaseProfile,
        animal_name: str,
        birth_year: int,
        species: AnimalSpecies,
        gender: AnimalGender,
        size: AnimalSize,
        sterilized: bool,
        vaccinated: bool,
        picture: str,
        state: AdoptionAnimalStates,
        publication_date: date | None,
        race: str | None = None,
        special_care: str | None = None,
        description: str | None = None,
    ) -> AdoptionAnimal:
        adoption_animal_id: str = uuid4().hex

        if actor_profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
            organizational_profile = cast(OrganizationalProfile, actor_profile)
            organization_id = organizational_profile.organization_id
        else:
            organization_id = None

        if publication_date:
            publication_date_not_none = publication_date
        else:
            publication_date_not_none = date_now()

        adoption_animal: AdoptionAnimal = AdoptionAnimal(
            entity_id=adoption_animal_id,
            animal_name=animal_name,
            birth_year=birth_year,
            species=species,
            gender=gender,
            size=size,
            sterilized=sterilized,
            vaccinated=vaccinated,
            profile_id=actor_profile.entity_id,
            picture=picture,
            organization_id=organization_id,
            state=state,
            publication_date=publication_date_not_none,
            race=race,
            special_care=special_care,
            description=description,
        )

        await self.animals_repository.add_animal(
            session=uow.session, adoption_animal=adoption_animal
        )

        return adoption_animal

    async def get_adoption_animal_by_id(
        self, uow: UnitOfWork, entity_id: str, get_all: bool = False
    ) -> AdoptionAnimal:
        adoption_animal: AdoptionAnimal | None = (
            await self.animals_repository.get_animal_by_id(
                session=uow.session, entity_id=entity_id, get_all=get_all
            )
        )

        if not adoption_animal:
            raise AnimalNotFoundByIdException(entity_id=entity_id)

        return adoption_animal

    async def get_all_adoption_animals(
        self,
        uow: UnitOfWork,
        species: list[AnimalSpecies] | None = None,
        limit: int | None = None,
        offset: int | None = 0,
        profile: BaseProfile | None = None,
        state: AdoptionAnimalStates | None = None,
    ) -> Sequence[AdoptionAnimal]:
        if profile and profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
            organization_id = cast(OrganizationalProfile, profile).organization_id

            return await self.animals_repository.get_animals_by_organizational_profile(
                session=uow.session,
                limit=limit,
                offset=offset,
                organization_id=organization_id,
                species=species,
            )

        return await self.animals_repository.get_animals(
            session=uow.session,
            limit=limit,
            offset=offset,
            species=species,
            state=state,
            profile_id=profile.entity_id if profile else None,
        )

    async def get_all_adoption_animals_count(
        self,
        uow: UnitOfWork,
        species: list[AnimalSpecies] | None = None,
        profile: BaseProfile | None = None,
        state: AdoptionAnimalStates | None = None,
    ) -> int:
        if profile and profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
            organization_id = cast(OrganizationalProfile, profile).organization_id

            return (
                await self.animals_repository.count_animals_by_organizational_profile(
                    session=uow.session,
                    organization_id=organization_id,
                    species=species,
                )
            )

        return await self.animals_repository.count_animals(
            session=uow.session,
            species=species,
            profile_id=profile.entity_id if profile else None,
            state=state,
        )

    async def edit_adoption_animal(
        self,
        uow: UnitOfWork,
        actor_profile: BaseProfile,
        adoption_animal: AdoptionAnimal,
        new_adoption_animal_data: ModifyAdoptionAnimalData,
    ) -> None:
        if actor_profile.profile_type == ProfileTypes.PERSONAL_PROFILE:
            self.__assert_profile_is_owner(
                profile=actor_profile, animal=adoption_animal
            )
        else:
            organizational_profile = cast(OrganizationalProfile, actor_profile)
            self.__assert_organization_is_owner(
                profile=organizational_profile, animal=adoption_animal
            )

        adoption_animal.animal_name = new_adoption_animal_data.animal_name
        adoption_animal.birth_year = new_adoption_animal_data.birth_year
        adoption_animal.species = new_adoption_animal_data.species
        adoption_animal.gender = new_adoption_animal_data.gender
        adoption_animal.size = new_adoption_animal_data.size
        adoption_animal.sterilized = new_adoption_animal_data.sterilized
        adoption_animal.vaccinated = new_adoption_animal_data.vaccinated
        adoption_animal.picture = new_adoption_animal_data.picture
        adoption_animal.race = new_adoption_animal_data.race
        adoption_animal.special_care = new_adoption_animal_data.special_care
        adoption_animal.description = new_adoption_animal_data.description
        adoption_animal.state = new_adoption_animal_data.state

        await uow.flush()

    async def delete_adoption_animal(
        self,
        uow: UnitOfWork,
        actor_profile: BaseProfile,
        adoption_animal: AdoptionAnimal,
    ) -> None:
        self.__assert_profile_is_owner(profile=actor_profile, animal=adoption_animal)

        adoption_animal.deleted = True
        self.__issue_adoption_animal_deleted_event(
            uow=uow, account=actor_profile.account, adoption_animal=adoption_animal
        )

    @staticmethod
    def __assert_profile_is_owner(profile: BaseProfile, animal: AdoptionAnimal) -> None:
        if animal.profile_id != profile.entity_id:
            raise AdoptionAnimalUnauthorizedAccessException(
                actor_account_id=profile.account.entity_id, animal_id=animal.entity_id
            )

    @staticmethod
    def __assert_organization_is_owner(
        profile: OrganizationalProfile, animal: AdoptionAnimal
    ) -> None:
        if animal.organization_id != profile.organization_id:
            raise AdoptionAnimalUnauthorizedAccessException(
                actor_account_id=profile.account.entity_id, animal_id=animal.entity_id
            )

    @staticmethod
    def __issue_adoption_animal_deleted_event(
        uow: UnitOfWork,
        account: Account,
        adoption_animal: AdoptionAnimal,
    ) -> None:
        # TODO: Test handlers for this
        uow.emit_event(
            AdoptionAnimalDeletedEvent(
                actor_account_id=account.entity_id,
                adoption_animal_id=adoption_animal.entity_id,
                issued=float_timestamp(),
            )
        )
