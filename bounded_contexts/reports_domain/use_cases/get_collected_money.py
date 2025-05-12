from typing import Sequence
from bounded_contexts.reports_domain.dataclasses import CollectedMoney
from bounded_contexts.reports_domain.services import ReportService
from bounded_contexts.reports_domain.use_cases.base_reports_use_case import (
    BaseReportsUseCase,
)
from bounded_contexts.reports_domain.views.collected_money_view import (
    CollectedMoneyViewFactory,
    CollectedMoneyListView,
)
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetCollectedMoneyUseCase(BaseReportsUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        reports_service: ReportService,
        collected_money_view_factory: CollectedMoneyViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils, report_service=reports_service
        )
        self.collected_money_view_factory = collected_money_view_factory

    @unit_of_work
    async def execute(
        self, organization_id: str | None, uow: UnitOfWork
    ) -> CollectedMoneyListView:
        collected_money: Sequence[CollectedMoney]

        collected_money = await self.report_service.get_collected_money(
            uow=uow,
            organization_id=organization_id,
        )

        return self.collected_money_view_factory.create_collected_money_list_view(
            campaign_donations=collected_money,
            total_count=len(collected_money),
        )
