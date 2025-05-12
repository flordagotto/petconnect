from typing import cast

from bounded_contexts.social_domain.entities import OrganizationalProfile
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import (
    OrganizationViewFactory,
    ProfileViewFactory,
)
from config.config import StaffConfig
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class VerifyOrganizationUseCase(BaseSocialUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        profile_service: ProfileService,
        profile_view_factory: ProfileViewFactory,
        organization_service: OrganizationService,
        organization_view_factory: OrganizationViewFactory,
        staff_config: StaffConfig,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            profile_service=profile_service,
            profile_view_factory=profile_view_factory,
            organization_service=organization_service,
            organization_view_factory=organization_view_factory,
        )
        self.staff_config = staff_config

    @unit_of_work
    async def execute(
        self, actor_account_id: str, organization_id: str, uow: UnitOfWork
    ) -> None:
        actor = await self.profile_service.get_profile_by_account_id(
            uow, actor_account_id
        )

        # Security checks
        assert actor.account.email.lower() == self.staff_config.staff_email.lower()

        organization = await self.organization_service.get_organization_by_id(
            uow, organization_id
        )

        profile = await self.profile_service.get_profile_by_account_id(
            uow=uow, account_id=organization.creator_account_id
        )

        organizational_profile = cast(OrganizationalProfile, profile)

        await self.organization_service.verify_organization(
            uow=uow, organization=organization, profile=organizational_profile
        )
