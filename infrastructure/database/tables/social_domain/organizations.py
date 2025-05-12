from sqlalchemy import Table, Column, MetaData, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.schema import SchemaItem
from bounded_contexts.social_domain.entities import Organization


def create_organizations_table(metadata: MetaData, accounts: Table) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True),
        Column("organization_name", String, unique=True, nullable=False),
        Column(
            "creator_account_id",
            String,
            ForeignKey(accounts.c.entity_id),
            nullable=False,
        ),
        Column("verified", Boolean, default=False, nullable=False),
        Column("verified_bank", Boolean, default=False, nullable=False),
        Column("phone_number", String, nullable=False),
        Column("social_media_url", String, nullable=True),
        Column("_merchant_data", JSONB, nullable=True),
    ]

    return Table("organizations", metadata, *columns)


def map_organizations_table(
    organizations_table: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(Organization, organizations_table)
