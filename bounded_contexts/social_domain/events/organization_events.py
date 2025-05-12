from infrastructure.uow_abstraction import Event


class OrganizationVerifiedEvent(Event):
    def __init__(
        self,
        actor_account_id: str,
        issued: float,
        email: str,
        profile_first_name: str,
        organization_name: str,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )

        self.email = email
        self.profile_first_name = profile_first_name
        self.organization_name = organization_name
