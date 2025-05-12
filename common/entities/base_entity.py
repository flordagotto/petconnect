from abc import ABC


class BaseDomainEntity(ABC):
    # The mother of all entities

    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id


class BaseDomainEntityTag(ABC):
    # Tag to represent the union of a many-to-many relationships between entities

    def __init__(
        self, left_entity: BaseDomainEntity, right_entity: BaseDomainEntity
    ) -> None:
        self.left_entity = left_entity
        self.right_entity = right_entity
