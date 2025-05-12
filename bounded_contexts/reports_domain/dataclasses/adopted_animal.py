from dataclasses import dataclass
from datetime import datetime


@dataclass
class AdoptedAnimal:
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
