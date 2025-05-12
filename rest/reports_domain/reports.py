from bounded_contexts.reports_domain.use_cases.get_adopted_animals import (
    GetAdoptedAnimalsUseCase,
)
from bounded_contexts.reports_domain.use_cases.get_collected_money import (
    GetCollectedMoneyUseCase,
)
from bounded_contexts.reports_domain.use_cases.get_lost_and_found_pets import (
    GetLostAndFoundPetsUseCase,
)
from bounded_contexts.reports_domain.views.adopted_animals_view import (
    AdoptedAnimalsListView,
)
from bounded_contexts.reports_domain.views.collected_money_view import (
    CollectedMoneyListView,
)
from bounded_contexts.reports_domain.views.lost_and_found_pets_view import (
    LostAndFoundPetsListView,
)
from infrastructure.rest import BaseAPIController


class ReportsController(BaseAPIController):
    async def get_adopted_animals(
        self, organization_id: str | None = None
    ) -> AdoptedAnimalsListView:
        get_adopted_animals_use_case: GetAdoptedAnimalsUseCase = (
            self.dependencies.resolve(GetAdoptedAnimalsUseCase)
        )

        return await get_adopted_animals_use_case.execute(
            GetAdoptedAnimalsUseCase.Request(organization_id=organization_id)
        )

    async def get_collected_money(
        self, organization_id: str | None = None
    ) -> CollectedMoneyListView:
        get_collected_money_use_case: GetCollectedMoneyUseCase = (
            self.dependencies.resolve(GetCollectedMoneyUseCase)
        )

        return await get_collected_money_use_case.execute(
            organization_id=organization_id
        )

    async def get_lost_and_found_pets(self) -> LostAndFoundPetsListView:
        get_lost_and_found_pets_use_case: GetLostAndFoundPetsUseCase = (
            self.dependencies.resolve(GetLostAndFoundPetsUseCase)
        )

        return await get_lost_and_found_pets_use_case.execute()

    def register_routes(self) -> None:
        PREFIX: str = "/reports"

        self._register_get_route(
            f"{PREFIX}/adopted_animals", method=self.get_adopted_animals
        )
        self._register_get_route(
            f"{PREFIX}/collected_money", method=self.get_collected_money
        )
        self._register_get_route(
            f"{PREFIX}/lost_and_found_pets", method=self.get_lost_and_found_pets
        )
