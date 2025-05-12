from datetime import datetime
from common.entities import BaseDomainEntity


class PetSight(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        pet_id: str,
        latitude: float,
        longitude: float,
        account_id: str | None,
        created_at: datetime,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.entity_id = entity_id
        self.pet_id = pet_id
        self.latitude = latitude
        self.longitude = longitude
        self.account_id = account_id
        self.created_at = created_at

    def __repr__(self) -> str:
        return (
            f"PetSight("
            f"entity_id={self.entity_id}, "
            f"latitude={self.latitude}, "
            f"longitude={self.longitude}, "
            f"created_at={self.created_at}, "
            f")"
        )
