from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.donations_domain.donation_campaigns import DonationCampaignsController


class DonationsRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        donations_controller: DonationCampaignsController = DonationCampaignsController(
            dependencies=self.dependencies
        )

        return [donations_controller]
