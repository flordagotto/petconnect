from abc import ABC, abstractmethod

from bounded_contexts.donations_domain.entities import MercadoPagoTransaction
from infrastructure.uow_abstraction.unit_of_work_module import Session


class MpTransactionsRepository(ABC):
    @abstractmethod
    async def add_transaction(
        self,
        session: Session,
        transaction: MercadoPagoTransaction,
    ) -> None:
        pass
