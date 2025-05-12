from datetime import date
from typing import Sequence, Dict
from pydantic import BaseModel
from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)


class PetView(BaseModel):
    entity_id: str
    animal_name: str
    birth_year: int
    species: AnimalSpecies
    gender: AnimalGender
    size: AnimalSize
    sterilized: bool
    vaccinated: bool
    picture: str
    qr_code: str
    profile_id: str
    lost: bool
    animal_type: str
    owner_name: str | None = None
    lost_date: date | None = None
    race: str | None = None
    special_care: str | None = None
    last_known_location: str | None = None
    last_known_latitude: float | None = None
    last_known_longitude: float | None = None


class OwnerView(BaseModel):
    name: str
    phone_number: str
    email: str
    social_media_url: str | None


class PetAndOwnerView(BaseModel):
    pet_view: PetView
    owner_view: OwnerView


class PetListView(BaseModel):
    items: Sequence[PetView]
    total_count: int


class PetAndOwnerListView(BaseModel):
    items: Sequence[PetAndOwnerView]
    total_count: int


class PetViewFactory:
    @staticmethod
    def create_pet_view(pet: Pet, owner_name: str | None = None) -> PetView:
        return PetView(
            entity_id=pet.entity_id,
            animal_name=pet.animal_name,
            birth_year=pet.birth_year,
            species=pet.species,
            gender=pet.gender,
            size=pet.size,
            sterilized=pet.sterilized,
            vaccinated=pet.vaccinated,
            lost=pet.lost,
            lost_date=pet.lost_date,
            profile_id=pet.profile_id,
            owner_name=owner_name,
            qr_code=pet.qr_code,
            picture=pet.picture,
            animal_type=pet.animal_type.value,
            race=pet.race,
            special_care=pet.special_care,
            last_known_location=pet.last_known_location,
            last_known_latitude=pet.last_known_latitude,
            last_known_longitude=pet.last_known_longitude,
        )

    @staticmethod
    def create_pet_list_view(pets: Dict[Pet, str], total_count: int) -> PetListView:
        pets_list_view: list[PetView] = []

        for pet, owner_name in pets.items():
            pets_list_view.append(
                PetViewFactory.create_pet_view(pet=pet, owner_name=owner_name)
            )
        return PetListView(items=pets_list_view, total_count=total_count)

    @staticmethod
    def create_pet_and_owner_view(
        pet: Pet,
        owner_name: str,
        owner_phone_number: str,
        owner_email: str,
        owner_social_media_url: str | None,
    ) -> PetAndOwnerView:
        return PetAndOwnerView(
            pet_view=PetView(
                entity_id=pet.entity_id,
                animal_name=pet.animal_name,
                birth_year=pet.birth_year,
                species=pet.species,
                gender=pet.gender,
                size=pet.size,
                sterilized=pet.sterilized,
                vaccinated=pet.vaccinated,
                lost=pet.lost,
                lost_date=pet.lost_date,
                profile_id=pet.profile_id,
                owner_name=owner_name,
                qr_code=pet.qr_code,
                picture=pet.picture,
                animal_type=pet.animal_type.value,
                race=pet.race,
                special_care=pet.special_care,
                last_known_location=pet.last_known_location,
                last_known_latitude=pet.last_known_latitude,
                last_known_longitude=pet.last_known_longitude,
            ),
            owner_view=OwnerView(
                name=owner_name,
                phone_number=owner_phone_number,
                email=owner_email,
                social_media_url=owner_social_media_url,
            ),
        )

    @staticmethod
    def create_pet_and_owner_list_view(
        pets_and_owners: Dict[Pet, OwnerView], total_count: int
    ) -> PetAndOwnerListView:
        pets_list_view: list[PetAndOwnerView] = []

        for pet, owner in pets_and_owners.items():
            pets_list_view.append(
                PetViewFactory.create_pet_and_owner_view(
                    pet=pet,
                    owner_name=owner.name,
                    owner_phone_number=owner.phone_number,
                    owner_email=owner.email,
                    owner_social_media_url=owner.social_media_url,
                )
            )
        return PetAndOwnerListView(items=pets_list_view, total_count=total_count)
