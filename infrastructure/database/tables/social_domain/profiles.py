from sqlalchemy import Table, Column, MetaData, String, ForeignKey, Enum, Date, Boolean
from sqlalchemy.orm import relationship
from bounded_contexts.auth.entities import Account
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    PersonalProfile,
    OrganizationalProfile,
)
from bounded_contexts.social_domain.enum import OrganizationRoles, ProfileTypes


# Docs on sqlalchemy inheritance:
# https://www.google.com/search?client=safari&rls=en&q=inheritance+sqlalchemy&ie=UTF-8&oe=UTF-8


# We'll use single table inheritance, for efficiency and ease of use.
def create_profiles_table(
    metadata: MetaData,
    accounts: Table,
    organizations: Table,
) -> Table:
    columns = [
        # BaseProfile attributes
        Column("entity_id", String, primary_key=True),
        Column("first_name", String, nullable=False),
        Column("surname", String, nullable=False),
        Column("phone_number", String, nullable=False),
        Column("account_id", String, ForeignKey(accounts.c.entity_id), nullable=False),
        Column("birthdate", Date),
        Column(
            "government_id", String
        ),  # Not null, but nullable because of inheritance
        # discriminator
        Column("profile_type", Enum(ProfileTypes), nullable=False),
        # PersonalProfile attributes
        # in the future...
        # OrganizationalProfile attributes
        Column("organization_role", Enum(OrganizationRoles), nullable=True),  # idem
        Column(
            "organization_id", ForeignKey(organizations.c.entity_id), nullable=True
        ),  # idem
        Column("verified_by_organization", Boolean, nullable=True),
        Column("social_media_url", String, nullable=True),
    ]

    return Table("profiles", metadata, *columns)  # type:ignore


def map_profiles_table(
    profiles_table: Table,
    mapper_registry,
) -> None:
    base = mapper_registry.map_imperatively(
        BaseProfile,
        profiles_table,
        polymorphic_on=profiles_table.c.profile_type,
        with_polymorphic=("*", profiles_table),
    )

    mapper_registry.map_imperatively(
        OrganizationalProfile,
        profiles_table,
        inherits=base,
        polymorphic_on=profiles_table.c.profile_type,
        polymorphic_identity=ProfileTypes.ORGANIZATIONAL_PROFILE,
        concrete=True,
        properties={
            "account": relationship(
                Account,
                uselist=False,
                lazy="joined",
                foreign_keys=[
                    profiles_table.c.account_id,
                ],
            ),
        },
    )

    mapper_registry.map_imperatively(
        PersonalProfile,
        profiles_table,
        inherits=base,
        polymorphic_on=profiles_table.c.profile_type,
        polymorphic_identity=ProfileTypes.PERSONAL_PROFILE,
        concrete=True,
        properties={
            "account": relationship(
                Account,
                uselist=False,
                lazy="joined",
                foreign_keys=[
                    profiles_table.c.account_id,
                ],
            ),
        },
    )
