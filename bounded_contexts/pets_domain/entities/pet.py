from datetime import date
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
    Animal,
)
from bounded_contexts.social_domain.enum import AnimalTypes


class Pet(Animal):
    def __init__(
        self,
        entity_id: str,
        animal_name: str,
        birth_year: int,
        species: AnimalSpecies,
        gender: AnimalGender,
        size: AnimalSize,
        sterilized: bool,
        vaccinated: bool,
        lost: bool,
        profile_id: str,
        qr_code: str,
        picture: str,
        lost_date: date | None = None,
        found_date: date | None = None,
        race: str | None = None,
        special_care: str | None = None,
        last_known_location: str | None = None,
        last_known_latitude: float | None = None,
        last_known_longitude: float | None = None,
        adoption_animal_id: str | None = None,
    ) -> None:
        super().__init__(
            entity_id=entity_id,
            animal_name=animal_name,
            birth_year=birth_year,
            species=species,
            gender=gender,
            size=size,
            sterilized=sterilized,
            vaccinated=vaccinated,
            picture=picture,
            race=race,
            special_care=special_care,
            profile_id=profile_id,
            animal_type=AnimalTypes.PET,
        )
        self.qr_code = qr_code
        self.lost = lost
        self.lost_date = lost_date
        self.found_date = found_date
        self.last_known_location = last_known_location
        self.last_known_latitude = last_known_latitude
        self.last_known_longitude = last_known_longitude
        self.adoption_animal_id = adoption_animal_id
