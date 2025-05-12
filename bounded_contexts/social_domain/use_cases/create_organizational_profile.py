from dataclasses import dataclass
from datetime import date
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.auth.views import AccountView
from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import (
    ProfileViewFactory,
    OrganizationalProfileView,
)
from bounded_contexts.social_domain.views.organization_views import (
    OrganizationViewFactory,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreateOrganizationalProfileUseCase(BaseSocialUseCase):
    @dataclass
    class Request:
        organization_id: str
        email: str
        password: str
        first_name: str
        surname: str
        phone_number: str
        government_id: str
        birthdate: date
        organization_role: OrganizationRoles

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
    ) -> OrganizationalProfileView:
        account_view: AccountView = await self.create_account_use_case.execute(
            CreateAccountUseCase.Request(
                email=request.email,
                password=request.password,
            ),
            uow=uow,
        )

        profile = await self.profile_service.create_organization_employee_profile(
            uow=uow,
            account=await self.accounts_service.get_account_by_id(
                uow=uow, account_id=account_view.entity_id
            ),
            first_name=request.first_name,
            surname=request.surname,
            phone_number=request.phone_number,
            government_id=request.government_id,
            organization_id=request.organization_id,
            birthdate=request.birthdate,
            organization_role=request.organization_role,
        )

        return self.profile_view_factory.create_organizational_profile_view(
            profile=profile
        )
