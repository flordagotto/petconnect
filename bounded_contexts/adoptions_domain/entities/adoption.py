from datetime import datetime
from common.entities import BaseDomainEntity


class Adoption(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        adoption_date: datetime,
        adoption_application_id: str,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.adoption_date = adoption_date
        self.adoption_application_id = adoption_application_id

    def __repr__(self) -> str:
        return f"Adoption(entity_id={self.entity_id}, date={self.adoption_date})"
