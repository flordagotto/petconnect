from sqlalchemy import Table, Column, MetaData, String, DateTime, ForeignKey
from sqlalchemy.sql.schema import SchemaItem

from bounded_contexts.adoptions_domain.entities.adoption import Adoption


def create_adoptions_table(
    metadata: MetaData,
    adoption_application: Table,
) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True, nullable=False),
        Column("adoption_date", DateTime(timezone=True), nullable=False),
        Column(
            "adoption_application_id",
            String,
            ForeignKey(adoption_application.c.entity_id),
            nullable=False,
        ),
    ]

    return Table("adoptions", metadata, *columns)


def map_adoptions_table(
    adoptions_table: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(
        Adoption,
        adoptions_table,
    )
