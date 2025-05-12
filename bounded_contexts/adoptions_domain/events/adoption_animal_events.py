from infrastructure.uow_abstraction import Event


class BaseAdoptionAnimalEvent(Event):
    def __init__(
        self, actor_account_id: str, adoption_animal_id: str, issued: float
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )
        self.adoption_animal_id = adoption_animal_id


class AdoptionAnimalDeletedEvent(BaseAdoptionAnimalEvent):
    pass
