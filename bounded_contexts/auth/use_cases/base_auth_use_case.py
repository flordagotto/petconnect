from bounded_contexts.auth.services import AccountsService
from bounded_contexts.auth.views import AccountViewFactory
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils


class BaseAuthUseCase(BaseUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        accounts_service: AccountsService,
        account_view_factory: AccountViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.accounts_service = accounts_service
        self.account_view_factory = account_view_factory
