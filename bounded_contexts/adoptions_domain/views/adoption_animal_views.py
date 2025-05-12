from datetime import date
from typing import Sequence
from pydantic import BaseModel

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)


class AdoptionAnimalView(BaseModel):
    entity_id: str
    animal_name: str
    birth_year: int
    species: AnimalSpecies
    gender: AnimalGender
    size: AnimalSize
    sterilized: bool
    vaccinated: bool
    picture: str
    profile_id: str
    state: AdoptionAnimalStates
    publication_date: date
    publicator_name: str
    deleted: bool = False
    organization_id: str | None = None
    race: str | None = None
    special_care: str | None = None
    description: str | None = None


class AdoptionAnimalListView(BaseModel):
    items: Sequence[AdoptionAnimalView]
    total_count: int


class AdoptionAnimalViewFactory:
    @staticmethod
    def create_adoption_animal_view(
        adoption_animal: AdoptionAnimal,
        publicator_name: str,
    ) -> AdoptionAnimalView:
        return AdoptionAnimalView(
            entity_id=adoption_animal.entity_id,
            animal_name=adoption_animal.animal_name,
            birth_year=adoption_animal.birth_year,
            species=adoption_animal.species,
            gender=adoption_animal.gender,
            size=adoption_animal.size,
            sterilized=adoption_animal.sterilized,
            vaccinated=adoption_animal.vaccinated,
            picture=adoption_animal.picture,
            profile_id=adoption_animal.profile_id,
            state=adoption_animal.state,
            publication_date=adoption_animal.publication_date,
            deleted=adoption_animal.deleted,
            organization_id=adoption_animal.organization_id,
            race=adoption_animal.race,
            special_care=adoption_animal.special_care,
            description=adoption_animal.description,
            publicator_name=publicator_name,
        )

    @staticmethod
    def create_adoption_animal_list_view(
        animals: Sequence[AdoptionAnimal],
        total_count: int,
        publicator_names: dict[str, str],
    ) -> AdoptionAnimalListView:
        adoption_animals_list_view: list[AdoptionAnimalView] = []

        for adoption_animal in animals:
            adoption_animals_list_view.append(
                AdoptionAnimalViewFactory.create_adoption_animal_view(
                    adoption_animal=adoption_animal,
                    publicator_name=publicator_names[adoption_animal.profile_id],
                )
            )

        return AdoptionAnimalListView(
            items=adoption_animals_list_view, total_count=total_count
        )
