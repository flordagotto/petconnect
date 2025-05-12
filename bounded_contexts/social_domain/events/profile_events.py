from bounded_contexts.social_domain.enum import OrganizationRoles
from infrastructure.uow_abstraction import Event


class PersonalProfileCreatedEvent(Event):
    def __init__(
        self,
        actor_account_id: str,
        issued: float,
        email: str,
        first_name: str,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )

        self.email = email
        self.first_name = first_name


class OrganizationalProfileCreatedEvent(Event):
    def __init__(
        self,
        actor_account_id: str,
        issued: float,
        email: str,
        first_name: str,
        organization_role: OrganizationRoles,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )

        self.email = email
        self.first_name = first_name
        self.organization_role = organization_role
