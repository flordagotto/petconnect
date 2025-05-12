from infrastructure.uow_abstraction import Event


class BaseAccountEvent(Event):
    def __init__(self, actor_account_id: str, issued: float, email: str) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )
        self.email = email


class PasswordResetRequestEvent(BaseAccountEvent):
    pass


class ResendVerificationMailRequestEvent(BaseAccountEvent):
    pass


class AccountVerifiedEvent(Event):
    def __init__(
        self,
        actor_account_id: str,
        issued: float,
        email: str,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )

        self.email = email
