from pydantic import BaseModel

from bounded_contexts.adoptions_domain.enum import (
    AdoptionApplicationStates,
    HousingTypes,
    OpenSpacesTypes,
)
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    ModifyAdoptionApplicationData,
)
from bounded_contexts.adoptions_domain.use_cases.create_adoption_application import (
    CreateAdoptionApplicationUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_application import (
    EditAdoptionApplicationUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.get_adoption_applications import (
    GetAdoptionApplicationsUseCase,
)
from bounded_contexts.adoptions_domain.views import (
    AdoptionApplicationView,
    AdoptionApplicationListView,
)
from bounded_contexts.auth.value_objects import TokenData
from infrastructure.rest import BaseAPIController, TokenDependency


class AdoptionApplicationController(BaseAPIController):
    class CreateAdoptionApplicationRequest(BaseModel):
        ever_had_pet: bool
        has_pet: bool
        type_of_housing: HousingTypes
        open_space: OpenSpacesTypes
        pet_time_commitment: str
        adoption_info: str
        animal_id: str
        safety_in_open_spaces: str | None = None
        animal_nice_to_others: str | None = None

    async def post(
        self, token: TokenDependency, body: CreateAdoptionApplicationRequest
    ) -> AdoptionApplicationView:
        token_data: TokenData = await self._get_token_data(token=token)

        create_adoption_application_use_case: CreateAdoptionApplicationUseCase = (
            self.dependencies.resolve(CreateAdoptionApplicationUseCase)
        )

        return await create_adoption_application_use_case.execute(
            CreateAdoptionApplicationUseCase.Request(
                ever_had_pet=body.ever_had_pet,
                has_pet=body.has_pet,
                type_of_housing=body.type_of_housing,
                open_space=body.open_space,
                pet_time_commitment=body.pet_time_commitment,
                adoption_info=body.adoption_info,
                adopter_account_id=token_data.account_id,
                animal_id=body.animal_id,
                safety_in_open_spaces=body.safety_in_open_spaces,
                animal_nice_to_others=body.animal_nice_to_others,
            )
        )

    class EditAdoptionApplicationRequest(BaseModel):
        entity_id: str
        state: AdoptionApplicationStates

    async def put(
        self, token: TokenDependency, body: EditAdoptionApplicationRequest
    ) -> AdoptionApplicationView:
        token_data: TokenData = await self._get_token_data(token=token)
        edit_adoption_application_use_case: EditAdoptionApplicationUseCase = (
            self.dependencies.resolve(EditAdoptionApplicationUseCase)
        )

        return await edit_adoption_application_use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=token_data.account_id,
                application_data=ModifyAdoptionApplicationData(
                    entity_id=body.entity_id,
                    state=body.state,
                ),
            )
        )

    # async def get(self, entity_id: str) -> AdoptionAnimalView:
    #     get_adoption_animal_use_case: GetAdoptionAnimalUseCase = (
    #         self.dependencies.resolve(GetAdoptionAnimalUseCase)
    #     )
    #
    #     return await get_adoption_animal_use_case.execute(entity_id)

    async def index_received_adoption_applications(
        self,
        token: TokenDependency,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> AdoptionApplicationListView:
        token_data: TokenData = await self._get_token_data(token=token)
        get_adoption_applications_use_case: GetAdoptionApplicationsUseCase = (
            self.dependencies.resolve(GetAdoptionApplicationsUseCase)
        )

        return await get_adoption_applications_use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=token_data.account_id,
                filter_by_sent_applications=False,
                limit=limit,
                offset=offset,
            )
        )

    async def index_sent_adoption_applications(
        self,
        token: TokenDependency,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> AdoptionApplicationListView:
        token_data: TokenData = await self._get_token_data(token=token)
        get_adoption_applications_use_case: GetAdoptionApplicationsUseCase = (
            self.dependencies.resolve(GetAdoptionApplicationsUseCase)
        )

        return await get_adoption_applications_use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=token_data.account_id,
                filter_by_sent_applications=True,
                limit=limit,
                offset=offset,
            )
        )

    # async def delete(self, token: TokenDependency, entity_id: str) -> None:
    #     token_data: TokenData = await self._get_token_data(token=token)
    #     delete_adoption_animal_use_case: DeleteAdoptionAnimalUseCase = (
    #         self.dependencies.resolve(DeleteAdoptionAnimalUseCase)
    #     )
    #     await delete_adoption_animal_use_case.execute(
    #         DeleteAdoptionAnimalUseCase.Request(
    #             entity_id=entity_id, actor_account_id=token_data.account_id
    #         )
    #     )

    def register_routes(self) -> None:
        PREFIX: str = "/adoptions/application"

        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_put_route(f"{PREFIX}", method=self.put)
        self._register_get_route(
            f"{PREFIX}/all/received", method=self.index_received_adoption_applications
        )
        self._register_get_route(
            f"{PREFIX}/all/sent", method=self.index_sent_adoption_applications
        )
