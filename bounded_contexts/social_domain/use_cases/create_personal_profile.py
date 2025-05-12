from dataclasses import dataclass
from datetime import date

from bounded_contexts.auth.services import AccountsService
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.auth.views import AccountView
from bounded_contexts.social_domain.entities import PersonalProfile
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import ProfileViewFactory, PersonalProfileView
from bounded_contexts.social_domain.views.organization_views import (
    OrganizationViewFactory,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreatePersonalProfileUseCase(BaseSocialUseCase):
    @dataclass
    class Request:
        account_request: CreateAccountUseCase.Request
        first_name: str
        surname: str
        phone_number: str
        government_id: str
        birthdate: date
        social_media_url: str | None = None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        profile_service: ProfileService,
        profile_view_factory: ProfileViewFactory,
        organization_service: OrganizationService,
        organization_view_factory: OrganizationViewFactory,
        accounts_service: AccountsService,
        create_account_use_case: CreateAccountUseCase,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            profile_service=profile_service,
            profile_view_factory=profile_view_factory,
            organization_service=organization_service,
            organization_view_factory=organization_view_factory,
        )

        self.accounts_service = accounts_service
        self.create_account_use_case = create_account_use_case

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> PersonalProfileView:
        account_view: AccountView = await self.create_account_use_case.execute(
            request=request.account_request,
            uow=uow,
        )

        profile: PersonalProfile = await self.profile_service.create_personal_profile(
            uow=uow,
            account=await self.accounts_service.get_account_by_id(
                uow=uow, account_id=account_view.entity_id
            ),
            first_name=request.first_name,
            surname=request.surname,
            phone_number=request.phone_number,
            government_id=request.government_id,
            birthdate=request.birthdate,
        )

        return self.profile_view_factory.create_personal_profile_view(profile=profile)
