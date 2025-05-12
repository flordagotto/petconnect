from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import ProfileViewFactory
from bounded_contexts.social_domain.views.organization_views import (
    OrganizationViewFactory,
    OrganizationView,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetOrganizationUseCase(BaseSocialUseCase):
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
    async def execute(
        self,
        entity_id: str,
        uow: UnitOfWork,
    ) -> OrganizationView:
        organization: Organization = (
            await self.organization_service.get_organization_by_id(
                uow=uow, entity_id=entity_id
            )
        )

        admin = await self.profile_service.get_organizational_profile_by_account_id(
            uow=uow,
            account_id=organization.creator_account_id,
        )

        admin_view = self.profile_view_factory.create_organizational_profile_view(
            profile=admin,
        )

        return self.organization_view_factory.create_organization_view(
            organization=organization,
            admin_view=admin_view,
        )
