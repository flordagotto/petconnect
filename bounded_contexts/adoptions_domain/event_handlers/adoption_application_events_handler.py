from typing import cast

from bounded_contexts.adoptions_domain.email import (
    AdoptionEmailSubjects,
    render_adoption_application_approved_template,
    render_adoption_application_rejected_template,
)
from bounded_contexts.adoptions_domain.entities import AdoptionApplication
from bounded_contexts.adoptions_domain.enum import AdoptionApplicationStates
from bounded_contexts.adoptions_domain.events import ApplicationStateUpdatedEvent
from bounded_contexts.adoptions_domain.services import (
    AdoptionAnimalsService,
    AdoptionApplicationService,
)
from bounded_contexts.social_domain.entities import OrganizationalProfile
from bounded_contexts.social_domain.enum import ProfileTypes
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from config import UrlConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import EventBus, make_unit_of_work


class AdoptionApplicationEventHandler:
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_animal_service: AdoptionAnimalsService,
        adoption_application_service: AdoptionApplicationService,
        profile_service: ProfileService,
        organization_service: OrganizationService,
        event_bus: EventBus,
        email_gateway: BaseEmailGateway,
        url_config: UrlConfig,
    ) -> None:
        self.repository_utils = repository_utils
        self.adoption_animal_service = adoption_animal_service
        self.adoption_application_service = adoption_application_service
        self.profile_service = profile_service
        self.organization_service = organization_service
        self.email_gateway = email_gateway
        self.url_config = url_config

        event_bus.on(
            ApplicationStateUpdatedEvent,
            self.__handle_application_state_updated_event,
        )

    async def __handle_application_state_updated_event(
        self, e: ApplicationStateUpdatedEvent
    ) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adoption_application: AdoptionApplication = (
                await self.adoption_application_service.get_application_by_id(
                    uow=uow, entity_id=e.adoption_application_id
                )
            )

            adopter_profile = await self.profile_service.get_profile(
                uow=uow, entity_id=adoption_application.adopter_profile_id
            )

            animal = await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow, entity_id=adoption_application.animal_id
            )

            adoption_giver_profile = (
                await self.profile_service.get_profile_by_account_id(
                    uow=uow, account_id=e.actor_account_id
                )
            )
            owner_name = adoption_giver_profile.first_name

            if (
                adoption_giver_profile.profile_type
                == ProfileTypes.ORGANIZATIONAL_PROFILE
            ):
                organizational_profile = cast(
                    OrganizationalProfile, adoption_giver_profile
                )
                organization = await self.organization_service.get_organization_by_id(
                    uow=uow, entity_id=organizational_profile.organization_id
                )
                owner_name = organization.organization_name

            if adoption_application.state == AdoptionApplicationStates.ACCEPTED:
                await self.__send_application_approved_email(
                    email=adopter_profile.account.email,
                    adopter_name=adopter_profile.first_name,
                    owner_name=owner_name,
                    animal_name=animal.animal_name,
                )
            else:
                await self.__send_application_rejected_email(
                    email=adopter_profile.account.email,
                    adopter_name=adopter_profile.first_name,
                    owner_name=owner_name,
                    animal_name=animal.animal_name,
                )

    async def __send_application_approved_email(
        self, email: str, adopter_name: str, owner_name: str, animal_name: str
    ) -> None:
        self.email_gateway.schedule_mail(
            recipient=email,
            subject=AdoptionEmailSubjects.ADOPTION_APPLICATION_STATUS_UPDATED.value,
            body=render_adoption_application_approved_template(
                profile_name=adopter_name,
                owner_name=owner_name,
                animal_name=animal_name,
            ),
        )

    async def __send_application_rejected_email(
        self, email: str, adopter_name: str, owner_name: str, animal_name: str
    ) -> None:
        self.email_gateway.schedule_mail(
            recipient=email,
            subject=AdoptionEmailSubjects.ADOPTION_APPLICATION_STATUS_UPDATED.value,
            body=render_adoption_application_rejected_template(
                profile_name=adopter_name,
                owner_name=owner_name,
                animal_name=animal_name,
            ),
        )
