from sqlalchemy import Table, Column, MetaData, String, ForeignKey, Boolean, Float
from sqlalchemy.sql.schema import SchemaItem
from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
    IndividualDonation,
)


def create_donations_table(
    metadata: MetaData,
    organizations: Table,
) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True, nullable=False),
        Column(
            "organization_id",
            String,
            ForeignKey(organizations.c.entity_id),
            nullable=False,
        ),
        Column(
            "campaign_picture",
            String,
            nullable=False,
        ),
        Column(
            "campaign_name",
            String,
            nullable=False,
        ),
        Column(
            "money_goal",
            Float,
            nullable=False,
        ),
        Column(
            "campaign_description",
            String,
            nullable=False,
        ),
        Column(
            "additional_information",
            String,
            nullable=False,
        ),
        Column("active", Boolean, nullable=False, default=True),
    ]

    return Table("donation_campaigns", metadata, *columns)


def create_individual_donation_tables(
    metadata: MetaData,
    donation_campaigns: Table,
    accounts: Table,
    mp_transactions: Table,
) -> Table:
    columns: list[SchemaItem] = [
        Column("entity_id", String, primary_key=True, nullable=False),
        Column(
            "donation_campaign_id",
            String,
            ForeignKey(donation_campaigns.c.entity_id),
            nullable=False,
        ),
        Column(
            "donor_account_id",
            String,
            ForeignKey(accounts.c.entity_id),
            nullable=False,
        ),
        Column(
            "amount",
            Float,
            nullable=False,
        ),
        Column(
            "mercadopago_fee",
            Float,
            nullable=False,
        ),
        Column(
            "application_fee",
            Float,
            nullable=False,
        ),
        Column(
            "mp_transaction_id",
            String,
            ForeignKey(mp_transactions.c.entity_id),
            nullable=False,
        ),
    ]

    return Table("individual_donations", metadata, *columns)


def map_donation_campaigns_table(
    donation_campaigns: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(
        DonationCampaign,
        donation_campaigns,
    )


def map_donations_table(
    individual_donations: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(
        IndividualDonation,
        individual_donations,
    )
