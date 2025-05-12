from dataclasses import dataclass
from typing import Sequence
from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import ProfileViewFactory
from bounded_contexts.social_domain.views.organization_views import (
    OrganizationViewFactory,
    OrganizationListView,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetOrganizationsUseCase(BaseSocialUseCase):
    @dataclass
    class Request:
        limit: int | None
        offset: int | None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        profile_service: ProfileService,
        profile_view_factory: ProfileViewFactory,
        organization_service: OrganizationService,
        organization_view_factory: OrganizationViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            profile_service=profile_service,
            profile_view_factory=profile_view_factory,
            organization_service=organization_service,
            organization_view_factory=organization_view_factory,
        )

    @unit_of_work
    async def execute(self, request: Request, uow: UnitOfWork) -> OrganizationListView:
        organizations: Sequence[
            Organization
        ] = await self.organization_service.get_all_organizations(
            uow=uow, limit=request.limit, offset=request.offset
        )

        total_count: int = await self.organization_service.get_all_organizations_count(
            uow=uow
        )

        admins = await self.profile_service.get_multiple_organizational_profiles_by_account_id(
            uow=uow,
            account_ids=[
                organization.creator_account_id for organization in organizations
            ],
        )

        admin_views = (
            self.profile_view_factory.create_multiple_organizational_profiles_view(
                organization_profiles=admins,
            )
        )

        return self.organization_view_factory.create_organization_list_view(
            organizations=organizations,
            total_count=total_count,
            admins_by_account_id={
                admin_view.account_id: admin_view for admin_view in admin_views
            },
        )
