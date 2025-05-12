from typing import Sequence

from pydantic import BaseModel

from bounded_contexts.reports_domain.dataclasses import CollectedMoney


class CollectedMoneyView(BaseModel):
    donation_campaign_id: str
    donation_campaign_name: str
    organization_name: str
    money_goal: float
    collected_amount: float
    application_collected_amount: float


class CollectedMoneyListView(BaseModel):
    items: Sequence[CollectedMoneyView]
    total_collected: float
    total_application_collected: float
    total_count: float


class CollectedMoneyViewFactory:
    @staticmethod
    def create_collected_money_view(
        campaign_donation: CollectedMoney,
    ) -> CollectedMoneyView:
        return CollectedMoneyView(
            donation_campaign_id=campaign_donation.donation_campaign_id,
            donation_campaign_name=campaign_donation.donation_campaign_name,
            organization_name=campaign_donation.organization_name,
            money_goal=campaign_donation.money_goal,
            collected_amount=campaign_donation.collected_amount,
            application_collected_amount=campaign_donation.application_collected_amount,
        )

    @staticmethod
    def create_collected_money_list_view(
        campaign_donations: Sequence[CollectedMoney], total_count: int
    ) -> CollectedMoneyListView:
        collected_money_list_view: list[CollectedMoneyView] = []
        total_collected: float = 0
        total_application_collected: float = 0

        for campaign_donation in campaign_donations:
            collected_money_list_view.append(
                CollectedMoneyViewFactory.create_collected_money_view(
                    campaign_donation=campaign_donation
                )
            )
            total_collected += campaign_donation.collected_amount
            total_application_collected += (
                campaign_donation.application_collected_amount
            )

        return CollectedMoneyListView(
            items=collected_money_list_view,
            total_collected=total_collected,
            total_application_collected=total_application_collected,
            total_count=total_count,
        )
