from sqlalchemy import Table, Column, MetaData, String, ForeignKey, Enum, DateTime
from sqlalchemy.sql.schema import SchemaItem
from bounded_contexts.donations_domain.entities.mercado_pago_response import (
    MercadoPagoTransaction,
)
from bounded_contexts.donations_domain.enum import MercadoPagoResponseStatuses


def create_mp_transactions_table(
    metadata: MetaData,
    donation_campaigns: Table,
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
            "status",
            Enum(MercadoPagoResponseStatuses),
            nullable=False,
        ),
        Column(
            "status_detail",
            String,
            nullable=False,
        ),
        Column(
            "date_approved",
            DateTime(timezone=True),
            nullable=True,
        ),
        Column(
            "payer_email",
            String,
            nullable=False,
        ),
        Column(
            "payer_identification_type",
            String,
            nullable=False,
        ),
        Column(
            "payer_identification_number",
            String,
            nullable=False,
        ),
        Column(
            "payer_name",
            String,
            nullable=False,
        ),
        Column(
            "payment_method_id",
            String,
            nullable=False,
        ),
        Column(
            "payment_type_id",
            String,
            nullable=False,
        ),
    ]

    return Table("mp_transactions", metadata, *columns)


def map_mp_transactions_table(
    mp_transactions: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(
        MercadoPagoTransaction,
        mp_transactions,
    )
