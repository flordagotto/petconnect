from datetime import datetime
from typing import Sequence

from pydantic import BaseModel

from bounded_contexts.reports_domain.dataclasses import AdoptedAnimal


class AdoptedAnimalView(BaseModel):
    adoption_id: str
    organization_id: str
    organization_name: str
    animal_id: str
    animal_name: str
    animal_species: str
    animal_birth_year: int
    animal_size: str
    adopter_id: str
    adopter_name: str
    start_date_for_adoption: datetime
    adoption_date: datetime


class AdoptedAnimalsListView(BaseModel):
    items: Sequence[AdoptedAnimalView]
    total_count: int


class AdoptedAnimalsViewFactory:
    @staticmethod
    def create_adopted_animal_view(animal: AdoptedAnimal) -> AdoptedAnimalView:
        return AdoptedAnimalView(
            adoption_id=animal.adoption_id,
            organization_id=animal.organization_id,
            organization_name=animal.organization_name,
            animal_id=animal.animal_id,
            animal_name=animal.animal_name,
            animal_species=animal.animal_species,
            animal_birth_year=animal.animal_birth_year,
            animal_size=animal.animal_size,
            adopter_id=animal.adopter_id,
            adopter_name=animal.adopter_name,
            start_date_for_adoption=animal.start_date_for_adoption,
            adoption_date=animal.adoption_date,
        )

    @staticmethod
    def create_adopted_animal_list_view(
        animals: Sequence[AdoptedAnimal], total_count: int
    ) -> AdoptedAnimalsListView:
        adopted_animals_list_view: list[AdoptedAnimalView] = []

        for animal in animals:
            adopted_animals_list_view.append(
                AdoptedAnimalsViewFactory.create_adopted_animal_view(animal=animal)
            )
        return AdoptedAnimalsListView(
            items=adopted_animals_list_view, total_count=total_count
        )
