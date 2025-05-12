from bounded_contexts.donations_domain.repositories import (
    DonationsRepository,
    MpTransactionsRepository,
)
from bounded_contexts.donations_domain.repositories.alchemy import (
    AlchemyMpTransactionsRepository,
)
from bounded_contexts.donations_domain.repositories.alchemy.alchemy_donations_repository import (
    AlchemyDonationsRepository,
)
from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
)
from bounded_contexts.donations_domain.services.mercado_pago_service import (
    MercadoPagoService,
)
from bounded_contexts.donations_domain.use_cases import (
    CreateDonationCampaignUseCase,
    GetDonationCampaignsUseCase,
    GetDonationCampaignUseCase,
    CloseDonationCampaignUseCase,
    GetMpPreferenceUseCase,
    CreateMpInformation,
)
from bounded_contexts.donations_domain.use_cases.donate_to_campaign import (
    DonateToCampaignUseCase,
)
from bounded_contexts.donations_domain.views import DonationsViewFactory
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.dependencies import BaseContextDependencies
from config import MercadoPagoConfig, ProjectConfig, UrlConfig
from infrastructure.database import RepositoryUtils


class DonationsContextDependencies(BaseContextDependencies):
    def _initialize_view_factories(self) -> None:
        donations_view_factory: DonationsViewFactory = DonationsViewFactory()

        self.dependencies.register(DonationsViewFactory, donations_view_factory)

    def _initialize_repositories(self) -> None:
        donations_repository: DonationsRepository = AlchemyDonationsRepository()

        self.dependencies.register(DonationsRepository, donations_repository)

        mp_transactions_repository: MpTransactionsRepository = (
            AlchemyMpTransactionsRepository()
        )

        self.dependencies.register(MpTransactionsRepository, mp_transactions_repository)

    def _initialize_services(self) -> None:
        donations_service: DonationsService = DonationsService(
            donations_repository=self.dependencies.resolve(DonationsRepository),
        )

        self.dependencies.register(DonationsService, donations_service)

        mp_config: MercadoPagoConfig = self.dependencies.resolve(
            ProjectConfig
        ).mp_config

        url_config: UrlConfig = self.dependencies.resolve(ProjectConfig).url_config

        mercado_pago_service: MercadoPagoService = MercadoPagoService(
            access_token=mp_config.access_token,
            client_id=mp_config.client_id,
            client_secret=mp_config.client_secret,
            frontend_url=url_config.frontend_url,
            mp_transactions_repository=self.dependencies.resolve(
                MpTransactionsRepository
            ),
        )

        self.dependencies.register(MercadoPagoService, mercado_pago_service)

    def _initialize_use_cases(self) -> None:
        create_donation_campaign_use_case = CreateDonationCampaignUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            donations_service=self.dependencies.resolve(DonationsService),
            donations_view_factory=self.dependencies.resolve(DonationsViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(
            CreateDonationCampaignUseCase, create_donation_campaign_use_case
        )

        donate_to_campaign = DonateToCampaignUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            donations_service=self.dependencies.resolve(DonationsService),
            donations_view_factory=self.dependencies.resolve(DonationsViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
            mercado_pago_service=self.dependencies.resolve(MercadoPagoService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(DonateToCampaignUseCase, donate_to_campaign)

        get_donation_campaigns = GetDonationCampaignsUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            donations_service=self.dependencies.resolve(DonationsService),
            donations_view_factory=self.dependencies.resolve(DonationsViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(GetDonationCampaignsUseCase, get_donation_campaigns)

        get_donation_campaign = GetDonationCampaignUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            donations_service=self.dependencies.resolve(DonationsService),
            donations_view_factory=self.dependencies.resolve(DonationsViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(GetDonationCampaignUseCase, get_donation_campaign)

        close_donation_campaign = CloseDonationCampaignUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            donations_service=self.dependencies.resolve(DonationsService),
            donations_view_factory=self.dependencies.resolve(DonationsViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(
            CloseDonationCampaignUseCase, close_donation_campaign
        )

        get_mp_preference = GetMpPreferenceUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            mercado_pago_service=self.dependencies.resolve(MercadoPagoService),
            donations_service=self.dependencies.resolve(DonationsService),
            organizations_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(GetMpPreferenceUseCase, get_mp_preference)

        create_mp_information = CreateMpInformation(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            donations_service=self.dependencies.resolve(DonationsService),
            profile_service=self.dependencies.resolve(ProfileService),
            donations_view_factory=self.dependencies.resolve(DonationsViewFactory),
            mercado_pago_service=self.dependencies.resolve(MercadoPagoService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(CreateMpInformation, create_mp_information)

    def _initialize_event_handlers(self) -> None:
        pass
