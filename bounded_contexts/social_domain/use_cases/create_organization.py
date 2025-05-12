from dataclasses import dataclass
from datetime import date

from bounded_contexts.auth.services import AccountsService
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.auth.views import AccountView
from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import ProfileViewFactory
from bounded_contexts.social_domain.views.organization_views import (
    OrganizationView,
    OrganizationViewFactory,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreateOrganizationUseCase(BaseSocialUseCase):
    @dataclass
    class Request:
        @dataclass
        class OrganizationAdminRequest:
            email: str
            password: str
            first_name: str
            surname: str
            phone_number: str
            government_id: str
            birthdate: date

        @dataclass
        class OrganizationRequest:
            organization_name: str
            phone_number: str
            social_media_url: str | None = None

        organization_admin_request: OrganizationAdminRequest
        organization_request: OrganizationRequest

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
    ) -> OrganizationView:
        # To have a consistent database state, in one unit of work we must create the admin account, admin actor_profile
        # and organization.

        # 1) Create account for org admin
        account_view: AccountView = await self.create_account_use_case.execute(
            CreateAccountUseCase.Request(
                email=request.organization_admin_request.email,
                password=request.organization_admin_request.password,
            ),
            uow=uow,
        )

        # 2) Create org itself
        organization: Organization = (
            await self.organization_service.create_organization(
                uow=uow,
                organization_name=request.organization_request.organization_name,
                creator_account_id=account_view.entity_id,
                phone_number=request.organization_request.phone_number,
                social_media_url=request.organization_request.social_media_url,
            )
        )

        # 3) Finish creating org admin actor_profile
        admin_account = await self.accounts_service.get_account_by_id(
            uow=uow,
            account_id=organization.creator_account_id,
        )

        admin_profile = await self.profile_service.create_organization_admin_profile(
            uow=uow,
            account=admin_account,
            first_name=request.organization_admin_request.first_name,
            surname=request.organization_admin_request.surname,
            phone_number=request.organization_admin_request.phone_number,
            government_id=request.organization_admin_request.government_id,
            organization_id=organization.entity_id,
            birthdate=request.organization_admin_request.birthdate,
        )

        admin_view = self.profile_view_factory.create_organizational_profile_view(
            profile=admin_profile,
        )

        return self.organization_view_factory.create_organization_view(
            organization=organization,
            admin_view=admin_view,
        )
