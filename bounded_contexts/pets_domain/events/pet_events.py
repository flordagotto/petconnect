from infrastructure.uow_abstraction import Event


class BasePetEvent(Event):
    def __init__(self, actor_account_id: str, pet_id: str, issued: float) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )
        self.pet_id = pet_id


class PetLostEvent(BasePetEvent):
    pass


class PetFoundEvent(BasePetEvent):
    pass


class PetSightingEvent(BasePetEvent):
    def __init__(
        self,
        issued: float,
        pet_id: str,
    ) -> None:
        super().__init__(
            actor_account_id=Event.EXTERNAL_ACTOR_ACCOUNT_ID,
            issued=issued,
            pet_id=pet_id,
        )
