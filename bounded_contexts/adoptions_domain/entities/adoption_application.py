from bounded_contexts.adoptions_domain.enum import (
    HousingTypes,
    AdoptionApplicationStates,
    OpenSpacesTypes,
)
from common.entities import BaseDomainEntity
from infrastructure.date_utils import datetime_now_tz


class AdoptionApplication(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        ever_had_pet: bool,
        has_pet: bool,
        type_of_housing: HousingTypes,
        pet_time_commitment: str,
        adoption_info: str,
        adopter_profile_id: str,
        animal_id: str,
        open_space: OpenSpacesTypes | None,
        safety_in_open_spaces: str | None,
        animal_nice_to_others: str | None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.application_date = datetime_now_tz()
        self.ever_had_pet = ever_had_pet
        self.has_pet = has_pet
        self.type_of_housing = type_of_housing
        self.open_space = open_space
        self.pet_time_commitment = pet_time_commitment
        self.adoption_info = adoption_info
        self.adopter_profile_id = adopter_profile_id
        self.animal_id = animal_id
        self.state = AdoptionApplicationStates.PENDING
        self.safety_in_open_spaces = safety_in_open_spaces
        self.animal_nice_to_others = animal_nice_to_others

    def __repr__(self) -> str:
        return (
            f"AdoptionApplication("
            f"entity_id={self.entity_id}, "
            f"application_date={self.application_date}), "
            f"ever_had_pet={self.ever_had_pet}), "
            f"has_pet={self.has_pet}), "
            f"type_of_housing={self.type_of_housing}), "
            f"open_space={self.open_space}), "
            f"pet_time_commitment={self.pet_time_commitment}), "
            f"adoption_info={self.adoption_info}), "
            f"state={self.state}), "
            f"safety_in_open_spaces={self.safety_in_open_spaces}), "
            f"animal_nice_to_others={self.animal_nice_to_others})"
        )
