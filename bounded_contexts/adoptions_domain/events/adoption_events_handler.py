from infrastructure.uow_abstraction import Event


class AnimalAdoptedEvent(Event):
    def __init__(
        self,
        actor_account_id: str,
        animal_id: str,
        issued: float,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )
        self.animal_id = animal_id
