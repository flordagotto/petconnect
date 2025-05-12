from sqlalchemy import (
    Table,
    Column,
    MetaData,
    String,
    ForeignKey,
    Integer,
    Boolean,
    Enum,
    Date,
    Double,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import SchemaItem
from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
    Animal,
    BaseProfile,
    Organization,
)
from bounded_contexts.social_domain.enum import AnimalTypes


def create_animals_table(
    metadata: MetaData,
    profiles: Table,
    organizations: Table,
) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True),
        Column("animal_name", String, nullable=False),
        Column("birth_year", Integer, nullable=False),
        Column("species", Enum(AnimalSpecies), nullable=False),
        Column("gender", Enum(AnimalGender), nullable=False),
        Column("size", Enum(AnimalSize), nullable=False),
        Column("sterilized", Boolean, nullable=False),
        Column("vaccinated", Boolean, nullable=False),
        Column("picture", String, nullable=False),
        Column("animal_type", Enum(AnimalTypes), nullable=False),
        Column(
            "profile_id",
            String,
            ForeignKey(profiles.c.entity_id),
            nullable=False,
            index=True,
        ),
        # Optional attributes
        Column("race", String, nullable=True),
        Column("special_care", String, nullable=True),
        Column("state", Enum(AdoptionAnimalStates), nullable=True),
        Column("description", String, nullable=True),
        Column(
            "organization_id",
            String,
            ForeignKey(organizations.c.entity_id),
            nullable=True,
            index=True,
        ),
        Column("publication_date", Date, nullable=True),
        Column("lost", Boolean, nullable=True),
        Column("lost_date", Date, nullable=True),
        Column("found_date", Date, nullable=True),
        Column("qr_code", String, nullable=True),
        Column("last_known_location", String, nullable=True),
        Column("last_known_latitude", Double, nullable=True),
        Column("last_known_longitude", Double, nullable=True),
        Column("adoption_animal_id", String, nullable=True),
        Column("deleted", Boolean, nullable=True),
    ]

    return Table("animals", metadata, *columns)


def map_animals_table(
    animals_table: Table,
    mapper_registry,
) -> None:
    base = mapper_registry.map_imperatively(
        Animal,
        animals_table,
        polymorphic_on=animals_table.c.animal_type,
        with_polymorphic=("*", animals_table),
    )

    mapper_registry.map_imperatively(
        AdoptionAnimal,
        animals_table,
        inherits=base,
        polymorphic_on=animals_table.c.animal_type,
        polymorphic_identity=AnimalTypes.ANIMAL_FOR_ADOPTION,
        concrete=True,
        properties={
            "profile": relationship(
                BaseProfile,
                uselist=False,
                lazy="joined",
                foreign_keys=[animals_table.c.profile_id],
            ),
            "organization": relationship(
                Organization,
                uselist=False,
                lazy="joined",
                foreign_keys=[animals_table.c.organization_id],
            ),
        },
    )

    mapper_registry.map_imperatively(
        Pet,
        animals_table,
        inherits=base,
        polymorphic_on=animals_table.c.animal_type,
        polymorphic_identity=AnimalTypes.PET,
        concrete=True,
        properties={
            "profile": relationship(
                BaseProfile,
                uselist=False,
                lazy="joined",
                foreign_keys=[animals_table.c.profile_id],
            )
        },
    )
