from abc import ABC, abstractmethod
from bounded_contexts.adoptions_domain.entities.adoption import Adoption
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AdoptionsRepository(ABC):
    @abstractmethod
    async def add_adoption(self, session: Session, adoption: Adoption) -> None:
        pass

    @abstractmethod
    async def get_adoption_by_id(
        self,
        session: Session,
        entity_id: str,
    ) -> Adoption | None:
        pass

    @abstractmethod
    async def get_adoption_by_application_id(
        self,
        session: Session,
        adoption_application_id: str,
    ) -> Adoption | None:
        pass

    # @abstractmethod
    # async def get_adoption_by_animal_id(
    #     self,
    #     session: Session,
    #     animal_id: str,
    # ) -> Adoption | None:
    #     pass
    #
    # @abstractmethod
    # async def get_adoptions(
    #     self,
    #     session: Session,
    #     limit: int | None = None,
    #     offset: int | None = 0,
    # ) -> Sequence[Adoption]:
    #     pass
    #
    # @abstractmethod
    # async def count_adoptions(
    #     self,
    #     session: Session,
    # ) -> int:
    #     pass
