from bounded_contexts.auth.repositories import AccountsRepository
from bounded_contexts.auth.repositories.alchemy import AlchemyAccountsRepository
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.auth.use_cases import (
    CreateAccountUseCase,
    LoginUseCase,
    VerifyAccountUseCase,
    RequestPasswordResetUseCase,
    ResendVerificationRequest,
)
from bounded_contexts.auth.use_cases.reset_password import ResetPasswordUseCase
from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.auth.views import AccountViewFactory
from common.dependencies import BaseContextDependencies
from config import ProjectConfig
from infrastructure.crypto import HashUtils, TokenUtils
from infrastructure.database import RepositoryUtils


class AuthContextDependencies(BaseContextDependencies):
    def _initialize_view_factories(self) -> None:
        account_view_factory: AccountViewFactory = AccountViewFactory()

        self.dependencies.register(AccountViewFactory, account_view_factory)

    def _initialize_repositories(self) -> None:
        accounts_repository: AccountsRepository = AlchemyAccountsRepository()

        self.dependencies.register(AccountsRepository, accounts_repository)

    def _initialize_services(self) -> None:
        accounts_service: AccountsService = AccountsService(
            crypto_config=self.dependencies.resolve(ProjectConfig).crypto,
            accounts_repository=self.dependencies.resolve(AccountsRepository),
            hash_utils=self.dependencies.resolve(HashUtils),
            token_utils=self.dependencies.resolve(TokenUtils[TokenData]),
        )

        self.dependencies.register(AccountsService, accounts_service)

    def _initialize_use_cases(self) -> None:
        sign_up: CreateAccountUseCase = CreateAccountUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            accounts_service=self.dependencies.resolve(AccountsService),
            account_view_factory=self.dependencies.resolve(AccountViewFactory),
        )

        self.dependencies.register(CreateAccountUseCase, sign_up)

        login: LoginUseCase = LoginUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            accounts_service=self.dependencies.resolve(AccountsService),
            account_view_factory=self.dependencies.resolve(AccountViewFactory),
        )

        self.dependencies.register(LoginUseCase, login)

        verify_account: VerifyAccountUseCase = VerifyAccountUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            accounts_service=self.dependencies.resolve(AccountsService),
            account_view_factory=self.dependencies.resolve(AccountViewFactory),
        )

        self.dependencies.register(VerifyAccountUseCase, verify_account)

        request_password_reset: RequestPasswordResetUseCase = (
            RequestPasswordResetUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                accounts_service=self.dependencies.resolve(AccountsService),
                account_view_factory=self.dependencies.resolve(AccountViewFactory),
            )
        )

        self.dependencies.register(RequestPasswordResetUseCase, request_password_reset)

        reset_password: ResetPasswordUseCase = ResetPasswordUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            accounts_service=self.dependencies.resolve(AccountsService),
            account_view_factory=self.dependencies.resolve(AccountViewFactory),
        )

        self.dependencies.register(ResetPasswordUseCase, reset_password)

        resend_verification_request = ResendVerificationRequest(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            accounts_service=self.dependencies.resolve(AccountsService),
            account_view_factory=self.dependencies.resolve(AccountViewFactory),
        )

        self.dependencies.register(
            ResendVerificationRequest, resend_verification_request
        )

    def _initialize_event_handlers(self) -> None:
        pass
