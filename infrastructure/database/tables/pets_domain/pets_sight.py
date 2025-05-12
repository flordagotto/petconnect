from sqlalchemy import (
    Table,
    Column,
    MetaData,
    String,
    ForeignKey,
    Double,
    DateTime,
)
from sqlalchemy.sql.schema import SchemaItem
from bounded_contexts.pets_domain.entities import PetSight


def create_pets_sight_table(metadata: MetaData, pets: Table, accounts: Table) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True),
        Column(
            "pet_id",
            String,
            ForeignKey(pets.c.entity_id, ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        Column("latitude", Double, nullable=False),
        Column("longitude", Double, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column(
            "account_id",
            String,
            ForeignKey(accounts.c.entity_id),
            nullable=True,
            index=True,
        ),
    ]

    return Table("pets_sight", metadata, *columns)


def map_pets_sight_table(
    pets_sight_table: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(
        PetSight,
        pets_sight_table,
    )
