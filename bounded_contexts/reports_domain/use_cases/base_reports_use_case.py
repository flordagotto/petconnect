from bounded_contexts.reports_domain.services import ReportService
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils


class BaseReportsUseCase(BaseUseCase):
    def __init__(
        self, repository_utils: RepositoryUtils, report_service: ReportService
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.report_service = report_service
