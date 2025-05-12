from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import registry

from infrastructure.database.tables.adoptions_domain.adoption_applications import (
    create_adoption_applications_table,
    map_adoptions_application_table,
)
from infrastructure.database.tables.adoptions_domain.adoptions import (
    create_adoptions_table,
    map_adoptions_table,
)
from infrastructure.database.tables.donations_domain.donations import (
    create_donations_table,
    create_individual_donation_tables,
    map_donation_campaigns_table,
    map_donations_table,
)
from infrastructure.database.tables.donations_domain.mp_transactions import (
    create_mp_transactions_table,
    map_mp_transactions_table,
)
from infrastructure.database.tables.social_domain.animals import (
    create_animals_table,
    map_animals_table,
)
from infrastructure.database.tables.auth_domain import (
    create_accounts_table,
    map_accounts_table,
)
from infrastructure.database.tables.pets_domain.pets_sight import (
    create_pets_sight_table,
    map_pets_sight_table,
)
from infrastructure.database.tables.social_domain import (
    create_organizations_table,
    map_organizations_table,
    create_profiles_table,
    map_profiles_table,
)


async def create_tables(
    metadata: MetaData,
    db_engine: AsyncEngine,
    orm_registry: registry,
) -> None:
    accounts_table = create_accounts_table(metadata=metadata)

    # Auth domain
    map_accounts_table(accounts_table=accounts_table, mapper_registry=orm_registry)

    organizations_table = create_organizations_table(
        metadata=metadata, accounts=accounts_table
    )

    # Social domain

    map_organizations_table(
        organizations_table=organizations_table, mapper_registry=orm_registry
    )

    profiles_table = create_profiles_table(
        metadata=metadata,
        accounts=accounts_table,
        organizations=organizations_table,
    )

    map_profiles_table(profiles_table=profiles_table, mapper_registry=orm_registry)

    #############################################################################################

    # Pets for adoption domain

    animals_table = create_animals_table(
        metadata=metadata, profiles=profiles_table, organizations=organizations_table
    )

    map_animals_table(animals_table=animals_table, mapper_registry=orm_registry)

    adoption_applications_table = create_adoption_applications_table(
        metadata=metadata,
        profiles=profiles_table,
        animals_table=animals_table,
    )

    map_adoptions_application_table(
        adoption_applications_table=adoption_applications_table,
        mapper_registry=orm_registry,
    )

    adoptions_table = create_adoptions_table(
        metadata=metadata, adoption_application=adoption_applications_table
    )

    map_adoptions_table(adoptions_table=adoptions_table, mapper_registry=orm_registry)

    # Lost pets domain

    pets_sight_table = create_pets_sight_table(
        metadata=metadata, pets=animals_table, accounts=accounts_table
    )

    map_pets_sight_table(
        pets_sight_table=pets_sight_table, mapper_registry=orm_registry
    )

    # Donations domain

    donation_campaigns_table = create_donations_table(
        metadata=metadata,
        organizations=organizations_table,
    )

    map_donation_campaigns_table(
        donation_campaigns=donation_campaigns_table,
        mapper_registry=orm_registry,
    )

    mp_transactions_table = create_mp_transactions_table(
        metadata=metadata,
        donation_campaigns=donation_campaigns_table,
    )

    map_mp_transactions_table(
        mp_transactions=mp_transactions_table,
        mapper_registry=orm_registry,
    )

    individual_donations_table = create_individual_donation_tables(
        metadata=metadata,
        donation_campaigns=donation_campaigns_table,
        accounts=accounts_table,
        mp_transactions=mp_transactions_table,
    )

    map_donations_table(
        individual_donations=individual_donations_table,
        mapper_registry=orm_registry,
    )

    async with db_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
