from dataclasses import dataclass

from bounded_contexts.social_domain.entities import BaseProfile
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import ProfileViewFactory
from bounded_contexts.social_domain.views.organization_views import (
    OrganizationViewFactory,
)
from bounded_contexts.social_domain.views.profile_views import BaseProfileView
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetProfileUseCase(BaseSocialUseCase):
    @dataclass
    class Request:
        account_id: str

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
    async def execute(self, request: Request, uow: UnitOfWork) -> BaseProfileView:
        profile: BaseProfile = await self.profile_service.get_profile_by_account_id(
            uow=uow, account_id=request.account_id
        )

        return self.profile_view_factory.create_profile_view(profile=profile)
