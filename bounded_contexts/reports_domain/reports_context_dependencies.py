from bounded_contexts.reports_domain.repositories import ReportsRepository
from bounded_contexts.reports_domain.repositories.alchemy.alchemy_reports_repository import (
    AlchemyReportsRepository,
)
from bounded_contexts.reports_domain.services import ReportService
from bounded_contexts.reports_domain.use_cases.get_adopted_animals import (
    GetAdoptedAnimalsUseCase,
)
from bounded_contexts.reports_domain.use_cases.get_collected_money import (
    GetCollectedMoneyUseCase,
)
from bounded_contexts.reports_domain.use_cases.get_lost_and_found_pets import (
    GetLostAndFoundPetsUseCase,
)
from bounded_contexts.reports_domain.views import AdoptedAnimalsViewFactory
from bounded_contexts.reports_domain.views.collected_money_view import (
    CollectedMoneyViewFactory,
)
from bounded_contexts.reports_domain.views.lost_and_found_pets_view import (
    LostAndFoundPetsViewFactory,
)
from common.dependencies import BaseContextDependencies
from infrastructure.database import RepositoryUtils


class ReportsContextDependencies(BaseContextDependencies):
    def _initialize_view_factories(self) -> None:
        adopted_animals_view_factory: AdoptedAnimalsViewFactory = (
            AdoptedAnimalsViewFactory()
        )

        self.dependencies.register(
            AdoptedAnimalsViewFactory, adopted_animals_view_factory
        )

        collected_money_view_factory: CollectedMoneyViewFactory = (
            CollectedMoneyViewFactory()
        )

        self.dependencies.register(
            CollectedMoneyViewFactory, collected_money_view_factory
        )

        lost_and_found_pets_view_factory: LostAndFoundPetsViewFactory = (
            LostAndFoundPetsViewFactory()
        )

        self.dependencies.register(
            LostAndFoundPetsViewFactory, lost_and_found_pets_view_factory
        )

    def _initialize_repositories(self) -> None:
        reports_repository: ReportsRepository = AlchemyReportsRepository()

        self.dependencies.register(ReportsRepository, reports_repository)

    def _initialize_services(self) -> None:
        reports_service: ReportService = ReportService(
            reports_repository=self.dependencies.resolve(ReportsRepository)
        )

        self.dependencies.register(ReportService, reports_service)

    def _initialize_use_cases(self) -> None:
        get_adopted_animals_use_case: GetAdoptedAnimalsUseCase = (
            GetAdoptedAnimalsUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                reports_service=self.dependencies.resolve(ReportService),
                adopted_animals_view_factory=self.dependencies.resolve(
                    AdoptedAnimalsViewFactory
                ),
            )
        )

        self.dependencies.register(
            GetAdoptedAnimalsUseCase, get_adopted_animals_use_case
        )

        get_collected_money_use_case: GetCollectedMoneyUseCase = (
            GetCollectedMoneyUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                reports_service=self.dependencies.resolve(ReportService),
                collected_money_view_factory=self.dependencies.resolve(
                    CollectedMoneyViewFactory
                ),
            )
        )

        self.dependencies.register(
            GetCollectedMoneyUseCase, get_collected_money_use_case
        )

        get_lost_and_found_pets_use_case: GetLostAndFoundPetsUseCase = (
            GetLostAndFoundPetsUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                reports_service=self.dependencies.resolve(ReportService),
                lost_and_found_pets_view_factory=self.dependencies.resolve(
                    LostAndFoundPetsViewFactory
                ),
            )
        )

        self.dependencies.register(
            GetLostAndFoundPetsUseCase, get_lost_and_found_pets_use_case
        )

    def _initialize_event_handlers(self) -> None:
        pass
