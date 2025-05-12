from typing import Type, Sequence

from sqlalchemy import func, select

from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
    IndividualDonation,
)
from bounded_contexts.donations_domain.repositories import DonationsRepository
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyDonationsRepository(DonationsRepository):
    def __init__(self) -> None:
        self.donation_campaign_model: Type[DonationCampaign] = DonationCampaign
        self.individual_donation_model: Type[IndividualDonation] = IndividualDonation

    async def add_donation_campaign(
        self, session: Session, donation_campaign: DonationCampaign
    ) -> None:
        session.add(donation_campaign)
        await session.flush([donation_campaign])

    async def add_individual_donation(
        self, session: Session, individual_donation: IndividualDonation
    ) -> None:
        session.add(individual_donation)
        await session.flush([individual_donation])

    async def get_donation_campaign_amount(
        self, session: Session, donation_campaign_id: str
    ) -> int:
        query = (
            select(
                func.sum(self.individual_donation_model.amount),  # type: ignore
            )
            .select_from(self.individual_donation_model)
            .where(self.individual_donation_model.donation_campaign_id == donation_campaign_id)  # type: ignore
        )

        result = await session.execute(query)
        amount = result.scalar()  # type: ignore
        return amount if amount else 0  # type: ignore

    async def find_donation_campaign(
        self,
        session: Session,
        donation_campaign_id: str,
    ) -> DonationCampaign | None:
        query = select(self.donation_campaign_model).where(
            self.donation_campaign_model.entity_id == donation_campaign_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_donation_campaigns(
        self,
        session: Session,
        active: bool,
        limit: int | None = None,
        offset: int | None = 0,
        organization_id: str | None = None,
    ) -> Sequence[DonationCampaign]:
        query = (
            select(self.donation_campaign_model)
            .order_by("campaign_name")
            .where(
                self.donation_campaign_model.active == active,  # type: ignore
            )
        )

        if organization_id is not None:
            query = query.where(
                self.donation_campaign_model.organization_id == organization_id,  # type: ignore
            )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_donation_campaigns(
        self,
        session: Session,
        active: bool,
        organization_id: str | None = None,
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(self.donation_campaign_model)
            .where(self.donation_campaign_model.active == active)  # type: ignore
        )

        if organization_id:
            query = query.where(self.donation_campaign_model.organization_id == organization_id)  # type: ignore

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_donation_campaign_amounts(
        self, session: Session, donation_campaign_ids: list[str]
    ) -> Sequence[tuple[str, int]]:
        query = (
            select(
                self.individual_donation_model.donation_campaign_id,  # type: ignore
                func.sum(self.individual_donation_model.amount),  # type: ignore
            )
            .select_from(self.individual_donation_model)
            .where(self.individual_donation_model.donation_campaign_id.in_(donation_campaign_ids))  # type: ignore
            .group_by(self.individual_donation_model.donation_campaign_id)  # type: ignore
        )

        result = await session.execute(query)
        return result.all()  # type: ignore

    async def get_individual_donation(
        self, session: Session, entity_id: str
    ) -> IndividualDonation | None:
        query = select(self.individual_donation_model).where(
            self.individual_donation_model.entity_id == entity_id  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()
