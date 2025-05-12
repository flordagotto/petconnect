from dataclasses import dataclass
from datetime import date
from typing import Sequence
from uuid import uuid4
from bounded_contexts.auth.entities import Account
from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.events import PetFoundEvent, PetLostEvent
from bounded_contexts.pets_domain.exceptions import PetUnauthorizedAccessException
from bounded_contexts.pets_domain.exceptions.owner_is_not_a_personal_profile_exception import (
    OwnerIsNotAPersonalProfileException,
)
from bounded_contexts.pets_domain.exceptions.pet_not_found_exception import (
    PetNotFoundByIdException,
    PetNotFoundByAdoptionAnimalIdException,
)
from bounded_contexts.pets_domain.repositories import PetsRepository
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.social_domain.enum import ProfileTypes
from config import UrlConfig
from infrastructure.date_utils import float_timestamp, date_now
from infrastructure.file_system import FileSystemGateway, FileSystemPrefix
from infrastructure.qr.qr_code import QRCodeGenerator
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class PetData:
    entity_id: str
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
    special_care: str | None = None
    qr_code: str | None = None
    race: str | None = None


@dataclass
class ModifyPetData:
    entity_id: str
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
    special_care: str | None = None
    race: str | None = None
    last_known_location: str | None = None
    last_known_latitude: float | None = None
    last_known_longitude: float | None = None


class PetService:
    def __init__(
        self,
        pets_repository: PetsRepository,
        qr_code: QRCodeGenerator,
        file_system_gateway: FileSystemGateway,
        url_config: UrlConfig,
    ) -> None:
        self.pets_repository = pets_repository
        self.qr_code = qr_code
        self.file_system_gateway = file_system_gateway
        self.url_config = url_config

    async def __create_qr_code_file(self, pet_id: str) -> None:
        qr_code: bytes = await self.qr_code.generate_qr_code(
            f"{self.url_config.frontend_url}/found-pet/{pet_id}/qr"
        )

        await self.file_system_gateway.save_file(
            prefix=FileSystemPrefix.QR,
            file_key=pet_id + ".png",
            file=qr_code,
        )

    async def regenerate_qr_code(self, _uow: UnitOfWork, pet: Pet) -> None:
        try:
            await self.file_system_gateway.delete_file(
                prefix=FileSystemPrefix.QR,
                file_key=pet.entity_id + ".png",
            )
        except:
            pass

        await self.__create_qr_code_file(pet_id=pet.entity_id)

        pet.qr_code = (
            f"{self.url_config.backend_url}/files/"
            f"{FileSystemPrefix.QR.value}/{pet.entity_id}.png"
        )

    async def create_pet(
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
        lost: bool,
        lost_date: date | None = None,
        race: str | None = None,
        special_care: str | None = None,
        adoption_animal_id: str | None = None,
    ) -> Pet:
        self.__assert_personal_profile(profile=actor_profile)

        pet_id: str = uuid4().hex

        if lost and lost_date is None:
            lost_date = date_now()

        await self.__create_qr_code_file(pet_id=pet_id)

        pet: Pet = Pet(
            entity_id=pet_id,
            animal_name=animal_name,
            birth_year=birth_year,
            species=species,
            gender=gender,
            size=size,
            sterilized=sterilized,
            vaccinated=vaccinated,
            lost=lost,
            lost_date=lost_date,
            profile_id=actor_profile.entity_id,
            qr_code=f"{self.url_config.backend_url}/files/{FileSystemPrefix.QR.value}/{pet_id}.png",
            picture=picture,
            race=race,
            special_care=special_care,
            adoption_animal_id=adoption_animal_id,
        )

        await self.pets_repository.add_pet(session=uow.session, pet=pet)

        return pet

    async def edit_pet(
        self,
        uow: UnitOfWork,
        actor_profile: BaseProfile,
        pet: Pet,
        new_pet_data: ModifyPetData,
    ) -> None:
        self.__assert_profile_is_owner(profile=actor_profile, pet=pet)

        was_lost: bool = pet.lost
        is_lost: bool = new_pet_data.lost

        pet.animal_name = new_pet_data.animal_name
        pet.birth_year = new_pet_data.birth_year
        pet.species = new_pet_data.species
        pet.gender = new_pet_data.gender
        pet.size = new_pet_data.size
        pet.sterilized = new_pet_data.sterilized
        pet.vaccinated = new_pet_data.vaccinated
        pet.picture = new_pet_data.picture
        pet.race = new_pet_data.race
        pet.special_care = new_pet_data.special_care
        pet.lost = new_pet_data.lost

        # If lost status changes, raise pet lost/found event
        if is_lost and not was_lost:
            # pet became lost
            self.__issue_pet_lost_event(uow=uow, account=actor_profile.account, pet=pet)

            if new_pet_data.lost_date is None:
                pet.lost_date = date_now()
            else:
                pet.lost_date = new_pet_data.lost_date

            pet.last_known_location = new_pet_data.last_known_location
            pet.last_known_latitude = new_pet_data.last_known_latitude
            pet.last_known_longitude = new_pet_data.last_known_longitude

        if not is_lost and was_lost:
            # pet was found
            self.__issue_pet_found_event(
                uow=uow, account=actor_profile.account, pet=pet
            )

            pet.lost_date = None
            pet.found_date = date_now()

            pet.last_known_location = None
            pet.last_known_latitude = None
            pet.last_known_longitude = None

        await uow.flush()

    async def get_pet_by_id(self, uow: UnitOfWork, entity_id: str) -> Pet:
        pet: Pet | None = await self.pets_repository.get_pet_by_id(
            session=uow.session, entity_id=entity_id
        )

        if not pet:
            raise PetNotFoundByIdException(entity_id=entity_id)

        return pet

    async def get_pet_by_adoption_animal_id(
        self, uow: UnitOfWork, adoption_animal_id: str
    ) -> Pet:
        pet: Pet | None = await self.pets_repository.get_pet_by_adoption_animal_id(
            session=uow.session, adoption_animal_id=adoption_animal_id
        )

        if not pet:
            raise PetNotFoundByAdoptionAnimalIdException(
                adoption_animal_id=adoption_animal_id
            )

        return pet

    async def get_all_pets(
        self,
        uow: UnitOfWork,
        limit: int | None = None,
        offset: int | None = 0,
        lost: bool | None = None,
        profile_id: str | None = None,
    ) -> Sequence[Pet]:
        pets: Sequence[Pet] = await self.pets_repository.get_pets(
            session=uow.session,
            limit=limit,
            offset=offset,
            lost=lost,
            profile_id=profile_id,
        )

        return pets

    async def get_all_pets_count(
        self, uow: UnitOfWork, lost: bool | None = None, profile_id: str | None = None
    ) -> int:
        return await self.pets_repository.count_pets(
            session=uow.session, lost=lost, profile_id=profile_id
        )

    async def delete_pet(self, uow: UnitOfWork, pet: Pet) -> None:
        await self.pets_repository.delete_pets(session=uow.session, pet=pet)

    def validate_user_can_delete_pet(
        self, actor_profile: BaseProfile, pet: Pet
    ) -> None:
        self.__assert_profile_is_owner(profile=actor_profile, pet=pet)

    def __assert_profile_is_owner(self, profile: BaseProfile, pet: Pet) -> None:
        # all owners are personal actor_profile
        self.__assert_personal_profile(profile=profile)

        if pet.profile_id != profile.entity_id:
            raise PetUnauthorizedAccessException(
                actor_account_id=profile.account.entity_id, pet_id=pet.entity_id
            )

    @staticmethod
    def __assert_personal_profile(profile: BaseProfile) -> None:
        if profile.profile_type is not ProfileTypes.PERSONAL_PROFILE:
            raise OwnerIsNotAPersonalProfileException(profile.entity_id)

    @staticmethod
    def __issue_pet_found_event(
        uow: UnitOfWork,
        account: Account,
        pet: Pet,
    ) -> None:
        # TODO: Test handlers for this
        uow.emit_event(
            PetFoundEvent(
                actor_account_id=account.entity_id,
                pet_id=pet.entity_id,
                issued=float_timestamp(),
            )
        )

    @staticmethod
    def __issue_pet_lost_event(
        uow: UnitOfWork,
        account: Account,
        pet: Pet,
    ) -> None:
        # TODO: Test handlers for this
        uow.emit_event(
            PetLostEvent(
                actor_account_id=account.entity_id,
                pet_id=pet.entity_id,
                issued=float_timestamp(),
            )
        )
