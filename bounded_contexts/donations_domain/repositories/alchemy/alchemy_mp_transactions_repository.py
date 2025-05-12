from typing import Type
from bounded_contexts.donations_domain.entities import MercadoPagoTransaction
from bounded_contexts.donations_domain.repositories import MpTransactionsRepository
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyMpTransactionsRepository(MpTransactionsRepository):
    def __init__(self) -> None:
        self.mp_transaction_model: Type[MercadoPagoTransaction] = MercadoPagoTransaction

    async def add_transaction(
        self,
        session: Session,
        transaction: MercadoPagoTransaction,
    ) -> None:
        session.add(transaction)
        await session.flush([transaction])
