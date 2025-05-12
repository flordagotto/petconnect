from sqlalchemy import (
    Table,
    Column,
    MetaData,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
)
from sqlalchemy.sql.schema import SchemaItem

from bounded_contexts.adoptions_domain.entities import AdoptionApplication
from bounded_contexts.adoptions_domain.enum import (
    HousingTypes,
    OpenSpacesTypes,
    AdoptionApplicationStates,
)


def create_adoption_applications_table(
    metadata: MetaData,
    profiles: Table,
    animals_table: Table,
) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True, nullable=False),
        Column("application_date", DateTime(timezone=True), nullable=False),
        Column("ever_had_pet", Boolean, nullable=False),
        Column("has_pet", Boolean, nullable=False),
        Column("type_of_housing", Enum(HousingTypes), nullable=False),
        Column("open_space", Enum(OpenSpacesTypes), nullable=True),
        Column("pet_time_commitment", String, nullable=False),
        Column("adoption_info", String, nullable=False),
        Column(
            "adopter_profile_id",
            String,
            ForeignKey(profiles.c.entity_id),
            nullable=False,
            index=True,
        ),
        Column(
            "animal_id",
            String,
            ForeignKey(animals_table.c.entity_id),
            nullable=False,
            index=True,
        ),
        Column("state", Enum(AdoptionApplicationStates), nullable=False),
        Column("safety_in_open_spaces", String, nullable=True),
        Column("animal_nice_to_others", String, nullable=True),
    ]

    return Table("adoption_applications", metadata, *columns)


def map_adoptions_application_table(
    adoption_applications_table: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(
        AdoptionApplication,
        adoption_applications_table,
    )
