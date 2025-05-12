from fastapi import HTTPException

from bounded_contexts.pets_domain.exceptions import (
    PetNotFoundException,
    OwnerIsNotAPersonalProfileException,
    PetUnauthorizedAccessException,
    PetNotFoundByIdException,
    SightForNotLostPetException,
    PetNotFoundByAdoptionAnimalIdException,
)
from rest.error_manager import BaseErrorManager, ErrorContainer
from rest.error_messages import MessagesConfig


class PetsErrorManager(BaseErrorManager):
    def __init__(self, messages_config: MessagesConfig) -> None:
        self.messages_config = messages_config

    def create_error_dictionary(self) -> ErrorContainer:
        return {
            PetNotFoundException: HTTPException(
                status_code=404,
                detail=self.messages_config.pets_messages.pet_not_found,
            ),
            PetNotFoundByIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.pets_messages.pet_not_found,
            ),
            OwnerIsNotAPersonalProfileException: HTTPException(
                status_code=400,
                detail=self.messages_config.pets_messages.owner_is_not_a_personal_profile,
            ),
            PetUnauthorizedAccessException: HTTPException(
                status_code=403,
                detail=self.messages_config.pets_messages.pet_unauthorized_access,
            ),
            SightForNotLostPetException: HTTPException(
                status_code=400,
                detail=self.messages_config.pets_messages.sight_for_not_lost_pet,
            ),
            PetNotFoundByAdoptionAnimalIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.pets_messages.pet_not_found,
            ),
        }
