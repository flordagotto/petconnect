from fastapi import HTTPException
from bounded_contexts.donations_domain.exceptions import (
    CollaboratorUnauthorizedCampaignManagementException,
    CampaignAlreadyFinishedException,
    DonationCampaignNotFoundByIdException,
    MoneyAmountNotValidException,
    OrganizationalProfileUnauthorizedToDonateException,
    MercadoPagoTransactionNotApprovedException,
    MercadoPagoPreferenceNotGeneratedException,
)
from bounded_contexts.donations_domain.exceptions.personal_profile_unauthorized_campaign_management_exception import (
    PersonalProfileUnauthorizedCampaignManagementException,
)
from rest.error_manager import BaseErrorManager, ErrorContainer
from rest.error_messages import MessagesConfig


class DonationsErrorManager(BaseErrorManager):
    def __init__(self, messages_config: MessagesConfig) -> None:
        self.messages_config = messages_config

    def create_error_dictionary(self) -> ErrorContainer:
        return {
            CollaboratorUnauthorizedCampaignManagementException: HTTPException(
                status_code=403,
                detail=self.messages_config.donations_messages.collaborator_unauthorized_campaign_management,
            ),
            CampaignAlreadyFinishedException: HTTPException(
                status_code=409,
                detail=self.messages_config.donations_messages.campaign_already_finished,
            ),
            DonationCampaignNotFoundByIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.donations_messages.donation_campaign_not_found,
            ),
            MoneyAmountNotValidException: HTTPException(
                status_code=409,
                detail=self.messages_config.donations_messages.money_amount_not_valid,
            ),
            PersonalProfileUnauthorizedCampaignManagementException: HTTPException(
                status_code=403,
                detail=self.messages_config.donations_messages.personal_profile_unauthorized_campaign_management,
            ),
            OrganizationalProfileUnauthorizedToDonateException: HTTPException(
                status_code=403,
                detail=self.messages_config.donations_messages.organizational_profile_unauthorized_to_donate,
            ),
            MercadoPagoPreferenceNotGeneratedException: HTTPException(
                status_code=400,
                detail=self.messages_config.donations_messages.mp_preference_not_generated,
            ),
            MercadoPagoTransactionNotApprovedException: HTTPException(
                status_code=403,
                detail=self.messages_config.donations_messages.mp_transaction_not_approved,
            ),
        }
