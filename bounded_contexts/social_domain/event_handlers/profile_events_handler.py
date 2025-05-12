from enum import Enum
from typing import cast

from bounded_contexts.auth.events import (
    ResendVerificationMailRequestEvent,
    PasswordResetRequestEvent,
    AccountVerifiedEvent,
)
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.social_domain.email import (
    SocialEmailSubjects,
    render_verify_account_template,
    render_reset_password_template,
)
from bounded_contexts.social_domain.email.social_email_templates import (
    render_account_verified_template,
)
from bounded_contexts.social_domain.entities import BaseProfile, OrganizationalProfile
from bounded_contexts.social_domain.enum import OrganizationRoles, ProfileTypes
from bounded_contexts.social_domain.events import (
    PersonalProfileCreatedEvent,
    OrganizationalProfileCreatedEvent,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from config import UrlConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import EventBus, make_unit_of_work


class VerifyAccountUrls(Enum):
    VERIFY_PERSONAL_PROFILE = "confirm-member-account"
    VERIFY_ORG_ADMIN = "confirm-foundation-account"
    VERIFY_ORG_MEMBER = "confirm-foundation-member-account"


class ProfileEventsHandler:
    def __init__(
        self,
        email_gateway: BaseEmailGateway,
        repository_utils: RepositoryUtils,
        accounts_service: AccountsService,
        profile_service: ProfileService,
        event_bus: EventBus,
        url_config: UrlConfig,
    ) -> None:
        self.email_gateway = email_gateway
        self.repository_utils = repository_utils
        self.accounts_service = accounts_service
        self.profile_service = profile_service
        self.url_config = url_config

        event_bus.on(
            PersonalProfileCreatedEvent, self.__handle_personal_profile_created_event
        )

        event_bus.on(
            OrganizationalProfileCreatedEvent,
            self.__handle_organizational_profile_created_event,
        )

        event_bus.on(
            ResendVerificationMailRequestEvent,
            self.__handle_resend_verification_mail_event,
        )

        event_bus.on(PasswordResetRequestEvent, self.__send_password_reset_email)

        event_bus.on(AccountVerifiedEvent, self.__handle_account_verified_event)

    async def __handle_personal_profile_created_event(
        self, e: PersonalProfileCreatedEvent
    ) -> None:
        await self.__send_verification_email(
            account_id=e.actor_account_id,
            email=e.email,
            profile_name=e.first_name,
            fe_route=VerifyAccountUrls.VERIFY_PERSONAL_PROFILE.value,
        )

    async def __handle_organizational_profile_created_event(
        self, e: OrganizationalProfileCreatedEvent
    ) -> None:
        await self.__send_verification_email(
            account_id=e.actor_account_id,
            email=e.email,
            profile_name=e.first_name,
            fe_route=VerifyAccountUrls.VERIFY_ORG_ADMIN.value
            if e.organization_role == OrganizationRoles.ADMIN
            else VerifyAccountUrls.VERIFY_ORG_MEMBER.value,
        )

    async def __handle_resend_verification_mail_event(
        self, e: ResendVerificationMailRequestEvent
    ) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile: BaseProfile | None = (
                await self.profile_service.find_profile_by_account_id(
                    uow=uow,
                    account_id=e.actor_account_id,
                )
            )

            if profile is None:
                return

            fe_route: str

            if profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
                organizational_profile: OrganizationalProfile = cast(
                    OrganizationalProfile,
                    profile,
                )

                fe_route = (
                    VerifyAccountUrls.VERIFY_ORG_ADMIN.value
                    if organizational_profile.organization_role
                    == OrganizationRoles.ADMIN
                    else VerifyAccountUrls.VERIFY_ORG_MEMBER.value
                )
            else:
                fe_route = VerifyAccountUrls.VERIFY_PERSONAL_PROFILE.value

        await self.__send_verification_email(
            account_id=e.actor_account_id,
            email=e.email,
            profile_name=profile.first_name,
            fe_route=fe_route,
        )

    async def __handle_account_verified_event(self, e: AccountVerifiedEvent) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile: BaseProfile | None = (
                await self.profile_service.find_profile_by_account_id(
                    uow=uow,
                    account_id=e.actor_account_id,
                )
            )

            if profile is None:
                return

            await self.__send_account_verified_email(
                email=e.email, profile_name=profile.first_name
            )

    async def __send_verification_email(
        self,
        account_id: str,
        email: str,
        profile_name: str,
        fe_route,
    ) -> None:
        verification_token: str = (
            await self.accounts_service.generate_account_verification_token(
                account_id=account_id,
            )
        )

        self.email_gateway.schedule_mail(
            recipient=email,
            subject=SocialEmailSubjects.VERIFY_ACCOUNT.value,
            body=render_verify_account_template(
                profile_name=profile_name,
                verify_account_url=f"{self.url_config.frontend_url}"
                f"/{fe_route}?verifyAccountToken={verification_token}",
            ),
        )

    async def __send_password_reset_email(self, e: PasswordResetRequestEvent) -> None:
        password_reset_token: str = (
            await self.accounts_service.generate_password_reset_token(
                account_id=e.actor_account_id,
            )
        )

        reset_link = f"{self.url_config.frontend_url}/recover-password?token={password_reset_token}"

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile = await self.profile_service.get_profile_by_account_id(
                uow=uow,
                account_id=e.actor_account_id,
            )

        self.email_gateway.schedule_mail(
            recipient=e.email,
            subject=SocialEmailSubjects.RESET_PASSWORD.value,
            body=render_reset_password_template(
                profile_name=profile.first_name,
                reset_password_url=reset_link,
            ),
        )

    async def __send_account_verified_email(
        self, email: str, profile_name: str
    ) -> None:
        self.email_gateway.schedule_mail(
            recipient=email,
            subject=SocialEmailSubjects.ACCOUNT_VERIFIED.value,
            body=render_account_verified_template(profile_name=profile_name),
        )
