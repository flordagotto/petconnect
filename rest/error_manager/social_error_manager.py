from fastapi import HTTPException
from bounded_contexts.social_domain.exceptions import (
    OrganizationAlreadyRegisteredException,
    ProfileAlreadyAssociatedToAccountException,
    ProfileNotFoundException,
    PersonalProfileNotFoundException,
    OrganizationalProfileNotFoundException,
    OrganizationNotFoundByNameException,
    OrganizationNotFoundByIdException,
)
from rest.error_manager import BaseErrorManager, ErrorContainer
from rest.error_messages import MessagesConfig


class SocialErrorManager(BaseErrorManager):
    def __init__(self, messages_config: MessagesConfig) -> None:
        self.messages_config = messages_config

    def create_error_dictionary(self) -> ErrorContainer:
        return {
            OrganizationAlreadyRegisteredException: HTTPException(
                status_code=409,
                detail=self.messages_config.social_messages.organization_already_registered,
            ),
            OrganizationNotFoundByNameException: HTTPException(
                status_code=404,
                detail=self.messages_config.social_messages.organization_not_found_by_name,
            ),
            ProfileAlreadyAssociatedToAccountException: HTTPException(
                status_code=409,
                detail=self.messages_config.social_messages.profile_already_associated,
            ),
            ProfileNotFoundException: HTTPException(
                status_code=404,
                detail=self.messages_config.social_messages.profile_not_found,
            ),
            PersonalProfileNotFoundException: HTTPException(
                status_code=404,
                detail=self.messages_config.social_messages.personal_profile_not_found,
            ),
            OrganizationalProfileNotFoundException: HTTPException(
                status_code=404,
                detail=self.messages_config.social_messages.organizational_profile_not_found,
            ),
            OrganizationNotFoundByIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.social_messages.organization_not_found_by_id,
            ),
        }
