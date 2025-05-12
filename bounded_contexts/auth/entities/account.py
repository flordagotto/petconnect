from common.entities import BaseDomainEntity


class Account(BaseDomainEntity):
    def __init__(
        self, entity_id: str, email: str, password: str, verified: bool
    ) -> None:
        super().__init__(entity_id=entity_id)
        self.email = email
        self.password = password
        self.verified = verified

    def __repr__(self) -> str:
        return f"Account(entity_id={self.entity_id}, email={self.email}, verified={self.verified})"
