from bounded_contexts.adoptions_domain.exceptions.base_animal_exception import (
    BaseAnimalException,
)


class AnimalSpeciesNotValidException(BaseAnimalException):
    # Not sure if we are going to need this
    def __init__(self, animal_species: list[str]) -> None:
        self.animal_species = animal_species

    def __str__(self) -> str:
        return f"Exception(animal_species={self.animal_species})"
