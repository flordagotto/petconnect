from pydantic import BaseModel
from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.pets_domain.use_cases import RegisterPetSightUseCase
from bounded_contexts.pets_domain.use_cases.get_most_recent_lost_pet_sights import (
    GetMostRecentLostPetSightsUseCase,
)
from bounded_contexts.pets_domain.use_cases.get_pet_sights import GetPetSightsUseCase
from bounded_contexts.pets_domain.views import PetSightView
from bounded_contexts.pets_domain.views.pet_sight_view import PetSightListView
from infrastructure.rest import BaseAPIController, OptionalTokenDependency


class PetSightController(BaseAPIController):
    class RegisterPetSightRequest(BaseModel):
        pet_id: str
        latitude: float
        longitude: float

    async def post(
        self, token: OptionalTokenDependency, body: RegisterPetSightRequest
    ) -> PetSightView:
        account_id: str | None = None

        if token is not None:
            token_data: TokenData = await self._get_token_data(token=token)
            account_id = token_data.account_id

        register_pet_sight_use_case: RegisterPetSightUseCase = (
            self.dependencies.resolve(RegisterPetSightUseCase)
        )

        return await register_pet_sight_use_case.execute(
            RegisterPetSightUseCase.Request(
                pet_id=body.pet_id,
                latitude=body.latitude,
                longitude=body.longitude,
                account_id=account_id,
            )
        )

    async def index_pet_sights(
        self,
        limit: int | None = None,
        offset: int | None = 0,
        pet_id: str | None = None,
        lost: bool | None = None,
    ) -> PetSightListView:
        get_pet_sights_use_case: GetPetSightsUseCase = self.dependencies.resolve(
            GetPetSightsUseCase
        )

        return await get_pet_sights_use_case.execute(
            GetPetSightsUseCase.Request(
                limit=limit, offset=offset, pet_id=pet_id, lost=lost
            )
        )

    async def index_most_recent_lost_pet_sights(
        self, limit: int | None = None, offset: int | None = 0
    ) -> PetSightListView:
        get_most_recent_lost_pet_sights_use_case: GetMostRecentLostPetSightsUseCase = (
            self.dependencies.resolve(GetMostRecentLostPetSightsUseCase)
        )

        return await get_most_recent_lost_pet_sights_use_case.execute(
            GetMostRecentLostPetSightsUseCase.Request(limit=limit, offset=offset)
        )

    def register_routes(self) -> None:
        PREFIX: str = "/pets_sight/pet_sight"

        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_get_route(f"{PREFIX}/all", method=self.index_pet_sights)
        self._register_get_route(
            f"{PREFIX}/all_recent_sights", method=self.index_most_recent_lost_pet_sights
        )
