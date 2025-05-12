from typing import Type
from sqlalchemy import select
from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.repositories import AccountsRepository
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyAccountsRepository(AccountsRepository):
    def __init__(self) -> None:
        self.model: Type[Account] = Account

    async def get_account_by_id(
        self, session: Session, account_id: str
    ) -> Account | None:
        query = select(self.model).where(
            self.model.entity_id == account_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def add_account(self, session: Session, account: Account) -> None:
        session.add(account)
        await session.flush([account])

    async def get_account_by_email(
        self, session: Session, email: str
    ) -> Account | None:
        query = select(self.model).where(
            self.model.email == email,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def flush(self, session: Session) -> None:
        await session.flush()
