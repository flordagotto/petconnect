from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.views import (
    OrganizationViewFactory,
    ProfileViewFactory,
)
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils


class BaseSocialUseCase(BaseUseCase):
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
        )

        self.profile_service = profile_service
        self.organization_service = organization_service

        self.profile_view_factory = profile_view_factory
        self.organization_view_factory = organization_view_factory
