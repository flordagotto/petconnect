from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
    IndividualDonation,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class DonationsRepository(ABC):
    @abstractmethod
    async def add_donation_campaign(
        self,
        session: Session,
        donation_campaign: DonationCampaign,
    ) -> None:
        pass

    @abstractmethod
    async def add_individual_donation(
        self,
        session: Session,
        individual_donation: IndividualDonation,
    ) -> None:
        pass

    @abstractmethod
    async def get_donation_campaign_amount(
        self,
        session: Session,
        donation_campaign_id: str,
    ) -> int:
        pass

    @abstractmethod
    async def find_donation_campaign(
        self,
        session: Session,
        donation_campaign_id: str,
    ) -> DonationCampaign | None:
        pass

    @abstractmethod
    async def get_donation_campaigns(
        self,
        session: Session,
        active: bool,
        limit: int | None = None,
        offset: int | None = 0,
        organization_id: str | None = None,
    ) -> Sequence[DonationCampaign]:
        pass

    @abstractmethod
    async def count_donation_campaigns(
        self,
        session: Session,
        active: bool,
        organization_id: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_donation_campaign_amounts(
        self, session: Session, donation_campaign_ids: list[str]
    ) -> Sequence[tuple[str, int]]:
        pass

    @abstractmethod
    async def get_individual_donation(
        self, session: Session, entity_id: str
    ) -> IndividualDonation | None:
        pass
