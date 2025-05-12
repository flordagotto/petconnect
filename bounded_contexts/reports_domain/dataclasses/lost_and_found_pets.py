from dataclasses import dataclass
from datetime import datetime


@dataclass
class LostAndFoundPets:
    pet_id: str
    pet_name: str
    pet_species: str
    pet_race: str
    amount_of_sights: int
    lost_date: datetime | None = None
    found_date: datetime | None = None
