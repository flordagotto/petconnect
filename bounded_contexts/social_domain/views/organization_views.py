from typing import Sequence

from pydantic import BaseModel
from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.views.profile_views import OrganizationalProfileView


class OrganizationView(BaseModel):
    entity_id: str
    organization_name: str
    creator_account_id: str
    verified: bool
    verified_bank: bool
    phone_number: str
    social_media_url: str | None = None
    admin: OrganizationalProfileView


class OrganizationListView(BaseModel):
    items: Sequence[OrganizationView]
    total_count: int


class OrganizationViewFactory:
    @staticmethod
    def create_organization_view(
        organization: Organization, admin_view: OrganizationalProfileView
    ) -> OrganizationView:
        return OrganizationView(
            entity_id=organization.entity_id,
            organization_name=organization.organization_name,
            verified=organization.verified,
            creator_account_id=organization.creator_account_id,
            verified_bank=organization.verified_bank,
            phone_number=organization.phone_number,
            social_media_url=organization.social_media_url,
            admin=admin_view,
        )

    @staticmethod
    def create_organization_list_view(
        organizations: Sequence[Organization],
        admins_by_account_id: dict[str, OrganizationalProfileView],
        total_count: int,
    ) -> OrganizationListView:
        organizations_list_view: list[OrganizationView] = []

        for organization in organizations:
            organizations_list_view.append(
                OrganizationViewFactory.create_organization_view(
                    organization=organization,
                    admin_view=admins_by_account_id[organization.creator_account_id],
                )
            )
        return OrganizationListView(
            items=organizations_list_view, total_count=total_count
        )
