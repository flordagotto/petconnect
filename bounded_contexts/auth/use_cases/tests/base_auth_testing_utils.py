from abc import ABC, abstractmethod
from dataclasses import dataclass
from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.services import AccountsService
from common.dependencies import DependencyContainer
from config import ProjectConfig
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class AccountData:
    account_id: str
    email: str
    password: str


class BaseAuthTestingUtils(ABC):
    async def create_account(
        self,
        uow: UnitOfWork,
        email: str,
        password: str,
        auto_verify: bool = True,
    ) -> AccountData:
        account: Account = await self.accounts_service.create_account(
            uow=uow,
            email=email,
            password=password,
        )

        if auto_verify:
            await self.verify_account(uow=uow, account_id=account.entity_id)

        return AccountData(
            account_id=account.entity_id,
            email=account.email,
            password=account.password,
        )

    async def verify_account(
        self,
        uow: UnitOfWork,
        account_id: str,
    ):
        await self.accounts_service.verify_account(
            uow=uow,
            verification_token=await self.accounts_service.generate_account_verification_token(
                account_id=account_id
            ),
        )

    async def get_account_by_id(
        self,
        uow: UnitOfWork,
        account_id: str,
    ) -> AccountData:
        account: Account = await self.accounts_service.get_account_by_id(
            uow=uow,
            account_id=account_id,
        )

        return AccountData(
            account_id=account.entity_id,
            email=account.email,
            password=account.password,
        )

    @property
    def project_config(self) -> ProjectConfig:
        return self.get_dependencies().resolve(ProjectConfig)

    @property
    def accounts_service(self) -> AccountsService:
        return self.get_dependencies().resolve(AccountsService)

    @abstractmethod
    def get_dependencies(self) -> DependencyContainer:
        pass
