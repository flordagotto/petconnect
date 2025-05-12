from enum import Enum

from bounded_contexts.social_domain.enum import AnimalTypes
from common.entities import BaseDomainEntity


class AnimalSpecies(Enum):
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


class AnimalGender(Enum):
    MALE = "male"
    FEMALE = "female"


class AnimalSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    BIG = "big"


class Animal(BaseDomainEntity):
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
        picture: str,
        animal_type: AnimalTypes,
        profile_id: str,
        race: str | None = None,
        special_care: str | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)
        self.animal_name = animal_name
        self.birth_year = birth_year
        self.species = species
        self.gender = gender
        self.size = size
        self.sterilized = sterilized
        self.vaccinated = vaccinated
        self.picture = picture
        self.animal_type = animal_type
        self.profile_id = profile_id
        self.race = race
        self.special_care = special_care
