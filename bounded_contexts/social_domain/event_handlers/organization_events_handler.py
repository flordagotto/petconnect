from bounded_contexts.social_domain.email import (
    SocialEmailSubjects,
    render_organization_verified_template,
)
from bounded_contexts.social_domain.events import (
    OrganizationVerifiedEvent,
)
from config import UrlConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import EventBus


class OrganizationEventsHandler:
    def __init__(
        self,
        email_gateway: BaseEmailGateway,
        repository_utils: RepositoryUtils,
        event_bus: EventBus,
        url_config: UrlConfig,
    ) -> None:
        self.email_gateway = email_gateway
        self.repository_utils = repository_utils
        self.url_config = url_config

        event_bus.on(
            OrganizationVerifiedEvent, self.__handle_organization_verified_event
        )

    async def __handle_organization_verified_event(
        self, e: OrganizationVerifiedEvent
    ) -> None:
        await self.__send_organization_verified_email(
            email=e.email,
            profile_name=e.profile_first_name,
            organization_name=e.organization_name,
        )

    async def __send_organization_verified_email(
        self,
        email: str,
        profile_name: str,
        organization_name: str,
    ) -> None:
        self.email_gateway.schedule_mail(
            recipient=email,
            subject=SocialEmailSubjects.ORGANIZATION_VERIFIED.value,
            body=render_organization_verified_template(
                profile_name=profile_name, organization_name=organization_name
            ),
        )
