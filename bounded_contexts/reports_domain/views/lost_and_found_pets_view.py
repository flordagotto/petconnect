from datetime import datetime
from typing import Sequence

from pydantic import BaseModel

from bounded_contexts.reports_domain.dataclasses.lost_and_found_pets import (
    LostAndFoundPets,
)


class LostAndFoundPetsView(BaseModel):
    pet_id: str
    pet_name: str
    pet_species: str
    pet_race: str
    amount_of_sights: int
    lost_date: datetime | None = None
    found_date: datetime | None = None


class LostAndFoundPetsListView(BaseModel):
    items: Sequence[LostAndFoundPetsView]
    total_count: int


class LostAndFoundPetsViewFactory:
    @staticmethod
    def create_lost_and_found_pets_view(
        lost_and_found_pet: LostAndFoundPets,
    ) -> LostAndFoundPetsView:
        return LostAndFoundPetsView(
            pet_id=lost_and_found_pet.pet_id,
            pet_name=lost_and_found_pet.pet_name,
            pet_species=lost_and_found_pet.pet_species,
            pet_race=lost_and_found_pet.pet_race,
            amount_of_sights=lost_and_found_pet.amount_of_sights,
            lost_date=lost_and_found_pet.lost_date,
            found_date=lost_and_found_pet.found_date,
        )

    @staticmethod
    def create_lost_and_found_pets_list_view(
        lost_and_found_pets: Sequence[LostAndFoundPets], total_count: int
    ) -> LostAndFoundPetsListView:
        lost_and_found_pets_list_view: list[LostAndFoundPetsView] = []

        for pet in lost_and_found_pets:
            lost_and_found_pets_list_view.append(
                LostAndFoundPetsViewFactory.create_lost_and_found_pets_view(
                    lost_and_found_pet=pet
                )
            )

        return LostAndFoundPetsListView(
            items=lost_and_found_pets_list_view,
            total_count=total_count,
        )
