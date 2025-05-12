from fastapi import HTTPException

from bounded_contexts.adoptions_domain.exceptions import (
    AnimalNotFoundException,
    AnimalNotFoundByIdException,
    AnimalSpeciesNotValidException,
    AdoptionAnimalUnauthorizedAccessException,
    AdoptionAnimalApplicationUnauthorizedAccessException,
    ApplicationNotFoundByIdException,
    ApplicationNotFoundByAnimalIdException,
    ApplicationByOrganizationNotValidException,
    AdoptionApplicationForOwnAnimalException,
    ProfileAlreadyAppliedException,
    AdoptionNotFoundByIdException,
    AdoptionNotFoundByApplicationIdException,
    AnimalAlreadyAdoptedException,
)
from rest.error_manager import BaseErrorManager, ErrorContainer
from rest.error_messages import MessagesConfig


class AdoptionsErrorManager(BaseErrorManager):
    def __init__(self, messages_config: MessagesConfig) -> None:
        self.messages_config = messages_config

    def create_error_dictionary(self) -> ErrorContainer:
        return {
            AnimalNotFoundException: HTTPException(
                status_code=404,
                detail=self.messages_config.adoptions_messages.adoption_animal_not_found,
            ),
            AnimalNotFoundByIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.adoptions_messages.adoption_animal_not_found,
            ),
            AnimalSpeciesNotValidException: HTTPException(
                status_code=400,
                detail=self.messages_config.adoptions_messages.animal_species_not_valid,
            ),
            AdoptionAnimalUnauthorizedAccessException: HTTPException(
                status_code=403,
                detail=self.messages_config.adoptions_messages.adoption_animal_unauthorized_access,
            ),
            AdoptionAnimalApplicationUnauthorizedAccessException: HTTPException(
                status_code=403,
                detail=self.messages_config.adoptions_messages.adoption_application_unauthorized_access,
            ),
            ApplicationNotFoundByIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.adoptions_messages.adoption_application_not_found,
            ),
            ApplicationNotFoundByAnimalIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.adoptions_messages.adoption_application_not_found,
            ),
            ApplicationByOrganizationNotValidException: HTTPException(
                status_code=400,
                detail=self.messages_config.adoptions_messages.application_by_organization_not_valid,
            ),
            AdoptionApplicationForOwnAnimalException: HTTPException(
                status_code=400,
                detail=self.messages_config.adoptions_messages.adoption_application_for_own_animal,
            ),
            ProfileAlreadyAppliedException: HTTPException(
                status_code=409,
                detail=self.messages_config.adoptions_messages.profile_already_applied,
            ),
            AdoptionNotFoundByIdException: HTTPException(
                status_code=409,
                detail=self.messages_config.adoptions_messages.adoption_not_found,
            ),
            AdoptionNotFoundByApplicationIdException: HTTPException(
                status_code=409,
                detail=self.messages_config.adoptions_messages.adoption_not_found,
            ),
            AnimalAlreadyAdoptedException: HTTPException(
                status_code=400,
                detail=self.messages_config.adoptions_messages.animal_already_adopted,
            ),
        }
