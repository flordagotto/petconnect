from abc import ABC, abstractmethod
from bounded_contexts.auth.entities import Account
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AccountsRepository(ABC):
    @abstractmethod
    async def get_account_by_id(
        self, session: Session, account_id: str
    ) -> Account | None:
        pass

    @abstractmethod
    async def add_account(self, session: Session, account: Account) -> None:
        pass

    @abstractmethod
    async def get_account_by_email(
        self, session: Session, email: str
    ) -> Account | None:
        pass

    # TODO: make this generic across al repos
    @abstractmethod
    async def flush(self, session: Session) -> None:
        """Flush all the entity changes, so they are visible throughout the unit of work before the commit."""
        pass
