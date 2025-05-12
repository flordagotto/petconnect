from sqlalchemy import Table, Column, MetaData, String, Boolean
from bounded_contexts.auth.entities import Account


def create_accounts_table(
    metadata: MetaData,
) -> Table:
    columns = [
        Column("entity_id", String, primary_key=True),
        # TODO: Regexes for validation
        Column("email", String, unique=True, nullable=False),
        Column("password", String, nullable=False),
        Column("verified", Boolean, nullable=False),
    ]

    return Table("accounts", metadata, *columns)  # type:ignore


def map_accounts_table(
    accounts_table: Table,
    mapper_registry,
) -> None:
    mapper_registry.map_imperatively(Account, accounts_table)
