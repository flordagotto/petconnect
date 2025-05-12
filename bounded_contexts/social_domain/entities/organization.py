from common.entities import BaseDomainEntity
from infrastructure.payment_gateway import MerchantData


class Organization(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        organization_name: str,
        creator_account_id: str,
        verified: bool,
        verified_bank: bool,
        phone_number: str,
        social_media_url: str | None = None,
        _merchant_data: dict | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.entity_id = entity_id
        self.organization_name = organization_name
        self.creator_account_id = creator_account_id
        self.verified = verified
        self.verified_bank = verified_bank
        self.social_media_url = social_media_url
        self.phone_number = phone_number
        self._merchant_data = _merchant_data

    @property
    def merchant_data(self) -> MerchantData | None:
        return (
            MerchantData.from_dict(self._merchant_data) if self._merchant_data else None
        )

    @merchant_data.setter
    def merchant_data(self, value: MerchantData | None) -> None:
        self._merchant_data = value.as_dict() if value else None

    def __repr__(self) -> str:
        return (
            f"Organization("
            f"entity_id={self.entity_id}, "
            f"name={self.organization_name}, "
            f"verified={self.verified}, "
            f"phone_number={self.phone_number}, "
            f"social_media_url={self.social_media_url} "
            f")"
        )
