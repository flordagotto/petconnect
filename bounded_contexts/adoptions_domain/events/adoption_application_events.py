from infrastructure.uow_abstraction import Event


class BaseAdoptionApplicationEvent(Event):
    def __init__(
        self, actor_account_id: str, issued: float, adoption_application_id: str
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )
        self.adoption_application_id = adoption_application_id


class ApplicationStateUpdatedEvent(BaseAdoptionApplicationEvent):
    def __init__(
        self,
        actor_account_id: str,
        issued: float,
        adoption_application_id: str,
        email: str,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
            adoption_application_id=adoption_application_id,
        )
        self.email = email
