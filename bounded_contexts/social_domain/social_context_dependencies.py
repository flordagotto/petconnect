from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.social_domain.event_handlers import (
    ProfileEventsHandler,
    OrganizationEventsHandler,
)
from bounded_contexts.social_domain.repositories import (
    OrganizationsRepository,
    ProfileRepository,
)
from bounded_contexts.social_domain.repositories.alchemy import (
    AlchemyOrganizationsRepository,
    AlchemyProfileRepository,
)
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import (
    CreateOrganizationUseCase,
    GetOrganizationsUseCase,
    GetOrganizationUseCase,
    GetProfileUseCase,
    CreateOrganizationalProfileUseCase,
    GetOrganizationProfilesUseCase,
    EditOrganizationMemberStatus,
    EditPersonalProfileUseCase,
    VerifyOrganizationUseCase,
)
from bounded_contexts.social_domain.use_cases.create_personal_profile import (
    CreatePersonalProfileUseCase,
)
from bounded_contexts.social_domain.views import (
    OrganizationViewFactory,
    ProfileViewFactory,
)
from common.dependencies import BaseContextDependencies
from config import ProjectConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import EventBus


class SocialContextDependencies(BaseContextDependencies):
    def _initialize_view_factories(self) -> None:
        profile_view_factory: ProfileViewFactory = ProfileViewFactory()

        self.dependencies.register(ProfileViewFactory, profile_view_factory)

        organization_view_factory: OrganizationViewFactory = OrganizationViewFactory()

        self.dependencies.register(OrganizationViewFactory, organization_view_factory)

        self.dependencies.register(OrganizationViewFactory, organization_view_factory)

    def _initialize_repositories(self) -> None:
        profile_repository: ProfileRepository = AlchemyProfileRepository()

        self.dependencies.register(ProfileRepository, profile_repository)

        organizations_repository: OrganizationsRepository = (
            AlchemyOrganizationsRepository()
        )

        self.dependencies.register(OrganizationsRepository, organizations_repository)

    def _initialize_services(self) -> None:
        profile_service: ProfileService = ProfileService(
            profile_repository=self.dependencies.resolve(ProfileRepository),
        )

        self.dependencies.register(ProfileService, profile_service)

        organizations_service: OrganizationService = OrganizationService(
            organizations_repository=self.dependencies.resolve(OrganizationsRepository),
        )

        self.dependencies.register(OrganizationService, organizations_service)

    def _initialize_use_cases(self) -> None:
        create_personal_profile: CreatePersonalProfileUseCase = (
            CreatePersonalProfileUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                profile_service=self.dependencies.resolve(ProfileService),
                profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
                organization_service=self.dependencies.resolve(OrganizationService),
                organization_view_factory=self.dependencies.resolve(
                    OrganizationViewFactory
                ),
                create_account_use_case=self.dependencies.resolve(CreateAccountUseCase),
                accounts_service=self.dependencies.resolve(AccountsService),
            )
        )

        self.dependencies.register(
            CreatePersonalProfileUseCase, create_personal_profile
        )

        create_organizational_profile: CreateOrganizationalProfileUseCase = (
            CreateOrganizationalProfileUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                profile_service=self.dependencies.resolve(ProfileService),
                profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
                organization_service=self.dependencies.resolve(OrganizationService),
                organization_view_factory=self.dependencies.resolve(
                    OrganizationViewFactory
                ),
                create_account_use_case=self.dependencies.resolve(CreateAccountUseCase),
                accounts_service=self.dependencies.resolve(AccountsService),
            )
        )

        self.dependencies.register(
            CreateOrganizationalProfileUseCase, create_organizational_profile
        )

        create_organization: CreateOrganizationUseCase = CreateOrganizationUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
            organization_service=self.dependencies.resolve(OrganizationService),
            organization_view_factory=self.dependencies.resolve(
                OrganizationViewFactory
            ),
            create_account_use_case=self.dependencies.resolve(CreateAccountUseCase),
            accounts_service=self.dependencies.resolve(AccountsService),
        )

        self.dependencies.register(CreateOrganizationUseCase, create_organization)

        get_organizations: GetOrganizationsUseCase = GetOrganizationsUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
            organization_service=self.dependencies.resolve(OrganizationService),
            organization_view_factory=self.dependencies.resolve(
                OrganizationViewFactory
            ),
        )

        self.dependencies.register(GetOrganizationsUseCase, get_organizations)

        get_organization: GetOrganizationUseCase = GetOrganizationUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
            organization_service=self.dependencies.resolve(OrganizationService),
            organization_view_factory=self.dependencies.resolve(
                OrganizationViewFactory
            ),
        )

        self.dependencies.register(GetOrganizationUseCase, get_organization)

        get_profile: GetProfileUseCase = GetProfileUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
            organization_service=self.dependencies.resolve(OrganizationService),
            organization_view_factory=self.dependencies.resolve(
                OrganizationViewFactory
            ),
        )

        self.dependencies.register(GetProfileUseCase, get_profile)

        get_organizational_profiles: GetOrganizationProfilesUseCase = (
            GetOrganizationProfilesUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                profile_service=self.dependencies.resolve(ProfileService),
                profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
                organization_service=self.dependencies.resolve(OrganizationService),
                organization_view_factory=self.dependencies.resolve(
                    OrganizationViewFactory
                ),
            )
        )

        self.dependencies.register(
            GetOrganizationProfilesUseCase, get_organizational_profiles
        )

        edit_organization_member_status: EditOrganizationMemberStatus = (
            EditOrganizationMemberStatus(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                profile_service=self.dependencies.resolve(ProfileService),
                profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
                organization_service=self.dependencies.resolve(OrganizationService),
                organization_view_factory=self.dependencies.resolve(
                    OrganizationViewFactory
                ),
            )
        )

        self.dependencies.register(
            EditOrganizationMemberStatus, edit_organization_member_status
        )

        edit_personal_profile: EditPersonalProfileUseCase = EditPersonalProfileUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
            organization_service=self.dependencies.resolve(OrganizationService),
            organization_view_factory=self.dependencies.resolve(
                OrganizationViewFactory
            ),
        )

        self.dependencies.register(EditPersonalProfileUseCase, edit_personal_profile)

        verify_organization: VerifyOrganizationUseCase = VerifyOrganizationUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
            organization_service=self.dependencies.resolve(OrganizationService),
            organization_view_factory=self.dependencies.resolve(
                OrganizationViewFactory
            ),
            staff_config=self.dependencies.resolve(ProjectConfig).staff_config,
        )

        self.dependencies.register(VerifyOrganizationUseCase, verify_organization)

    def _initialize_event_handlers(self) -> None:
        profile_events_handler = ProfileEventsHandler(
            accounts_service=self.dependencies.resolve(AccountsService),
            email_gateway=self.dependencies.resolve(BaseEmailGateway),
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            profile_service=self.dependencies.resolve(ProfileService),
            url_config=self.dependencies.resolve(ProjectConfig).url_config,
            event_bus=self.dependencies.resolve(EventBus),
        )

        self.dependencies.register(ProfileEventsHandler, profile_events_handler)

        organization_events_handler = OrganizationEventsHandler(
            email_gateway=self.dependencies.resolve(BaseEmailGateway),
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            url_config=self.dependencies.resolve(ProjectConfig).url_config,
            event_bus=self.dependencies.resolve(EventBus),
        )

        self.dependencies.register(
            OrganizationEventsHandler, organization_events_handler
        )
