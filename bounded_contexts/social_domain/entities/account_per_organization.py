from bounded_contexts.auth.entities import Account
from bounded_contexts.social_domain.entities import Organization
from common.entities import BaseDomainEntityTag


class AccountPerOrganization(BaseDomainEntityTag):
    def __init__(
        self,
        organization: Organization,
        account: Account,
        # Not definite
        role_id: int,
    ) -> None:
        super().__init__(
            left_entity=organization,
            right_entity=account,
        )

        self.organization = organization
        self.account = account
        self.role_id = role_id

    def __repr__(self) -> str:
        return f"AccountPerOrganization(role_id={self.role_id})"
