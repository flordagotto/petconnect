from typing import Type, Sequence
from sqlalchemy import select, func
from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.repositories import OrganizationsRepository
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyOrganizationsRepository(OrganizationsRepository):
    def __init__(self) -> None:
        self.model: Type[Organization] = Organization

    async def get_organization_by_name(
        self, session: Session, organization_name: str
    ) -> Organization | None:
        query = select(self.model).where(
            self.model.organization_name == organization_name,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def add_organization(
        self, session: Session, organization: Organization
    ) -> None:
        session.add(organization)
        await session.flush([organization])

    async def get_organizations(
        self, session: Session, limit: int | None = None, offset: int | None = 0
    ) -> Sequence[Organization]:
        query = select(self.model).order_by(
            self.model.organization_name  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_organizations(self, session: Session) -> int:
        query = func.count().select().select_from(self.model)

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_organization_by_id(
        self, session: Session, entity_id: str
    ) -> Organization | None:
        query = select(self.model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_multiple_organizations_by_id(
        self, session: Session, organization_ids: list[str]
    ) -> Sequence[Organization]:
        query = select(self.model).where(
            self.model.entity_id.in_(organization_ids),  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().all()
