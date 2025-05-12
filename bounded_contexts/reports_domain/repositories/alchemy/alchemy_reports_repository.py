from typing import Sequence

from sqlalchemy import text

from bounded_contexts.reports_domain.dataclasses import AdoptedAnimal, CollectedMoney
from bounded_contexts.reports_domain.dataclasses.lost_and_found_pets import (
    LostAndFoundPets,
)
from bounded_contexts.reports_domain.repositories.reports_repository import (
    ReportsRepository,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyReportsRepository(ReportsRepository):
    def __init__(self) -> None:
        pass

    async def get_adopted_animals(
        self, session: Session, organization_id: str | None = None
    ) -> Sequence[AdoptedAnimal]:
        txt_query = (
            "SELECT ad.entity_id AS adoption_id, a.organization_id, o.organization_name, a.entity_id AS animal_id, a.animal_name, a.species AS animal_species, a.birth_year AS animal_birth_year, a.size AS animal_size, "
            "ap.adopter_profile_id AS adopter_id, concat(p.first_name, ' ', p.surname) AS adopter_name, a.publication_date AS start_date_for_adoption, ad.adoption_date "
            "FROM animals a "
            "JOIN animals a1 ON a.entity_id = a1.adoption_animal_id "
            "JOIN adoption_applications ap ON ap.animal_id = a.entity_id "
            "JOIN adoptions ad ON ad.adoption_application_id = ap.entity_id "
            "JOIN profiles p ON p.entity_id = ap.adopter_profile_id "
            "JOIN organizations o ON o.entity_id = a.organization_id "
            "WHERE a.animal_type = 'ANIMAL_FOR_ADOPTION' "
        )

        if organization_id is not None:
            txt_query += "AND a.organization_id = :organization_id"

        query = text(txt_query)
        params = {"organization_id": organization_id}

        result = await session.execute(query, params)
        rows = result.fetchall()

        data = [dict(zip(result.keys(), row)) for row in rows]

        animals = [
            AdoptedAnimal(
                row["adoption_id"],
                row["organization_id"],
                row["organization_name"],
                row["animal_id"],
                row["animal_name"],
                row["animal_species"],
                row["animal_birth_year"],
                row["animal_size"],
                row["adopter_id"],
                row["adopter_name"],
                row["start_date_for_adoption"],
                row["adoption_date"],
            )
            for row in data
        ]
        return animals

    async def get_collected_money(
        self, session: Session, organization_id: str | None
    ) -> Sequence[CollectedMoney]:
        txt_query = (
            "SELECT dc.entity_id AS donation_campaign_id, dc.campaign_name AS donation_campaign_name, "
            "dc.money_goal, dc.active AS campaign_is_active, sum(ind.amount) AS collected_amount, "
            "sum(ind.application_fee) AS application_collected_amount, org.organization_name "
            "FROM donation_campaigns dc "
            "JOIN individual_donations ind ON dc.entity_id = ind.donation_campaign_id "
            "JOIN organizations org ON org.entity_id = dc.organization_id "
        )

        params = {}

        if organization_id is not None:
            txt_query += " WHERE org.entity_id = :organization_id "
            params = {"organization_id": organization_id}

        txt_query += " GROUP BY dc.entity_id, org.organization_name "

        query = text(txt_query)
        result = await session.execute(query, params)
        rows = result.fetchall()

        data = [dict(zip(result.keys(), row)) for row in rows]

        collected_money = [
            CollectedMoney(
                row["donation_campaign_id"],
                row["donation_campaign_name"],
                row["organization_name"],
                row["money_goal"],
                row["collected_amount"],
                row["application_collected_amount"],
                row["campaign_is_active"],
            )
            for row in data
        ]
        return collected_money

    async def get_lost_and_found_pets(
        self, session: Session
    ) -> Sequence[LostAndFoundPets]:
        txt_query = (
            "SELECT a.entity_id AS pet_id, a.animal_name AS pet_name, a.species AS pet_species, a.race AS pet_race, "
            "COUNT(ps.pet_id) AS amount_of_sights, a.lost_date, a.found_date "
            "FROM animals a "
            "LEFT JOIN pets_sight ps ON a.entity_id = ps.pet_id "
            "WHERE a.animal_type = 'PET' "
            "GROUP BY a.entity_id "
            "HAVING COUNT(ps.pet_id) > 0 OR a.lost = true"
        )

        query = text(txt_query)
        result = await session.execute(query)
        rows = result.fetchall()

        data = [dict(zip(result.keys(), row)) for row in rows]

        lost_and_found_pets = [
            LostAndFoundPets(
                row["pet_id"],
                row["pet_name"],
                row["pet_species"],
                row["pet_race"],
                row["amount_of_sights"],
                row["lost_date"],
                row["found_date"],
            )
            for row in data
        ]
        return lost_and_found_pets
