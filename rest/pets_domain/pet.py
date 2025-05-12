from datetime import date

from pydantic import BaseModel
from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.pets_domain.services import ModifyPetData
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.use_cases import (
    CreatePetUseCase,
    EditPetUseCase,
    GetPetUseCase,
    GetPetsUseCase,
    DeletePetUseCase,
    RegenerateQrCodesUseCase,
)
from bounded_contexts.pets_domain.views import PetView, PetListView, PetAndOwnerView
from infrastructure.rest import BaseAPIController, TokenDependency


class PetController(BaseAPIController):
    class CreatePetRequest(BaseModel):
        animal_name: str
        birth_year: int
        species: AnimalSpecies
        gender: AnimalGender
        size: AnimalSize
        sterilized: bool
        vaccinated: bool
        lost: bool
        picture: str
        race: str | None = None
        special_care: str | None = None

    async def post(self, token: TokenDependency, body: CreatePetRequest) -> PetView:
        token_data: TokenData = await self._get_token_data(token=token)

        create_pet_use_case: CreatePetUseCase = self.dependencies.resolve(
            CreatePetUseCase
        )

        return await create_pet_use_case.execute(
            CreatePetUseCase.Request(
                actor_account_id=token_data.account_id,
                animal_name=body.animal_name,
                birth_year=body.birth_year,
                species=body.species,
                gender=body.gender,
                size=body.size,
                sterilized=body.sterilized,
                vaccinated=body.vaccinated,
                lost=body.lost,
                race=body.race,
                special_care=body.special_care,
                picture=body.picture,
            )
        )

    class EditPetRequest(BaseModel):
        entity_id: str
        animal_name: str
        birth_year: int
        species: AnimalSpecies
        gender: AnimalGender
        size: AnimalSize
        sterilized: bool
        vaccinated: bool
        lost: bool
        picture: str
        lost_date: date | None = None
        race: str | None = None
        special_care: str | None = None
        last_known_location: str | None = None
        last_known_latitude: float | None = None
        last_known_longitude: float | None = None

    async def put(self, token: TokenDependency, body: EditPetRequest) -> PetView:
        token_data: TokenData = await self._get_token_data(token=token)

        edit_pet_use_case: EditPetUseCase = self.dependencies.resolve(EditPetUseCase)

        return await edit_pet_use_case.execute(
            EditPetUseCase.Request(
                actor_account_id=token_data.account_id,
                pet_data=ModifyPetData(
                    entity_id=body.entity_id,
                    animal_name=body.animal_name,
                    birth_year=body.birth_year,
                    species=body.species,
                    gender=body.gender,
                    size=body.size,
                    sterilized=body.sterilized,
                    vaccinated=body.vaccinated,
                    lost=body.lost,
                    lost_date=body.lost_date,
                    picture=body.picture,
                    race=body.race,
                    special_care=body.special_care,
                    last_known_location=body.last_known_location,
                    last_known_latitude=body.last_known_latitude,
                    last_known_longitude=body.last_known_longitude,
                ),
            )
        )

    class GetPetRequest(BaseModel):
        entity_id: str

    async def get(self, entity_id: str) -> PetAndOwnerView:
        get_pet_use_case: GetPetUseCase = self.dependencies.resolve(GetPetUseCase)

        return await get_pet_use_case.execute(entity_id)

    async def get_by_profile(
        self, profile_id: str, limit: int | None = None, offset: int | None = 0
    ) -> PetListView:
        raise NotImplementedError()

    async def index_pets(
        self,
        limit: int | None = None,
        offset: int | None = 0,
        lost: bool | None = None,
        profile_id: str | None = None,
    ) -> PetListView:
        get_pets_use_case: GetPetsUseCase = self.dependencies.resolve(GetPetsUseCase)

        return await get_pets_use_case.execute(
            GetPetsUseCase.Request(
                limit=limit, offset=offset, lost=lost, profile_id=profile_id
            )
        )

    async def delete(self, token: TokenDependency, entity_id: str) -> None:
        token_data: TokenData = await self._get_token_data(token=token)
        delete_pets_use_case: DeletePetUseCase = self.dependencies.resolve(
            DeletePetUseCase
        )
        await delete_pets_use_case.execute(
            DeletePetUseCase.Request(
                entity_id=entity_id, actor_account_id=token_data.account_id
            )
        )

    async def post_regenerate_qr_codes(self) -> None:
        regenerate_qr_codes: RegenerateQrCodesUseCase = self.dependencies.resolve(
            RegenerateQrCodesUseCase
        )

        await regenerate_qr_codes.execute()

    def register_routes(self) -> None:
        PREFIX: str = "/pets/pet"

        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_put_route(f"{PREFIX}", method=self.put)
        self._register_get_route(f"{PREFIX}", method=self.get)
        self._register_get_route(f"{PREFIX}/all", method=self.index_pets)
        self._register_get_route(
            f"{PREFIX}/get_pet_by_profile_id", method=self.get_by_profile
        )
        self._register_delete_route(f"{PREFIX}", method=self.delete)

        self._register_post_route(
            f"{PREFIX}/regenerate_qr_codes", method=self.post_regenerate_qr_codes
        )
