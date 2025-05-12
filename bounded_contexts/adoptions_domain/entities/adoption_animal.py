from datetime import date

from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.social_domain.entities import (
    AnimalGender,
    AnimalSpecies,
    AnimalSize,
    Animal,
)
from bounded_contexts.social_domain.enum import AnimalTypes


class AdoptionAnimal(Animal):
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
        profile_id: str,
        picture: str,
        state: AdoptionAnimalStates,
        publication_date: date,
        deleted: bool = False,
        organization_id: str | None = None,
        race: str | None = None,
        special_care: str | None = None,
        description: str | None = None,
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
            animal_type=AnimalTypes.ANIMAL_FOR_ADOPTION,
            race=race,
            special_care=special_care,
            profile_id=profile_id,
        )
        self.organization_id = organization_id
        self.publication_date = publication_date
        self.deleted = deleted
        self.state = state
        self.description = description

    def __repr__(self) -> str:
        return (
            f"Animal("
            f"entity_id={self.entity_id}, "
            f"name={self.animal_name}, "
            f"birth_year={self.birth_year}, "
            f"species={self.species}, "
            f"gender={self.gender}, "
            f"size={self.size}, "
            f"sterilized={self.sterilized}, "
            f"vaccinated={self.vaccinated}, "
            f"state={self.state}, "
            f"publication_date={self.publication_date}, "
            f"deleted={self.deleted}, "
            f"race={self.race}, "
            f"special_care={self.special_care})"
        )
