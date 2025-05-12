from datetime import date

from fastapi import Query
from pydantic import BaseModel

from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    ModifyAdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases import (
    CreateAdoptionAnimalUseCase,
    DeleteAdoptionAnimalUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_animal import (
    EditAdoptionAnimalUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.get_adoption_animal import (
    GetAdoptionAnimalUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.get_adoption_animals import (
    GetAdoptionAnimalsUseCase,
)
from bounded_contexts.adoptions_domain.views import (
    AdoptionAnimalView,
    AdoptionAnimalListView,
)
from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from infrastructure.date_utils import date_now
from infrastructure.rest import BaseAPIController, TokenDependency


class AdoptionAnimalController(BaseAPIController):
    class CreateAdoptionAnimalRequest(BaseModel):
        animal_name: str
        birth_year: int
        species: AnimalSpecies
        gender: AnimalGender
        size: AnimalSize
        sterilized: bool
        vaccinated: bool
        picture: str
        race: str | None = None
        publication_date: date | None = date_now()
        special_care: str | None = None
        description: str | None = None

    async def post(
        self, token: TokenDependency, body: CreateAdoptionAnimalRequest
    ) -> AdoptionAnimalView:
        token_data: TokenData = await self._get_token_data(token=token)

        create_adoption_animal_use_case: CreateAdoptionAnimalUseCase = (
            self.dependencies.resolve(CreateAdoptionAnimalUseCase)
        )

        return await create_adoption_animal_use_case.execute(
            CreateAdoptionAnimalUseCase.Request(
                account_id=token_data.account_id,
                animal_name=body.animal_name,
                birth_year=body.birth_year,
                species=body.species,
                gender=body.gender,
                size=body.size,
                sterilized=body.sterilized,
                vaccinated=body.vaccinated,
                race=body.race,
                special_care=body.special_care,
                picture=body.picture,
                description=body.description,
                publication_date=body.publication_date,
            )
        )

    class EditAdoptionAnimalRequest(BaseModel):
        entity_id: str
        animal_name: str
        birth_year: int
        species: AnimalSpecies
        gender: AnimalGender
        size: AnimalSize
        sterilized: bool
        vaccinated: bool
        picture: str
        state: AdoptionAnimalStates
        race: str | None = None
        special_care: str | None = None
        description: str | None = None

    async def put(
        self, token: TokenDependency, body: EditAdoptionAnimalRequest
    ) -> AdoptionAnimalView:
        token_data: TokenData = await self._get_token_data(token=token)
        edit_adoption_animal_use_case: EditAdoptionAnimalUseCase = (
            self.dependencies.resolve(EditAdoptionAnimalUseCase)
        )

        return await edit_adoption_animal_use_case.execute(
            EditAdoptionAnimalUseCase.Request(
                actor_account_id=token_data.account_id,
                animal_data=ModifyAdoptionAnimalData(
                    entity_id=body.entity_id,
                    animal_name=body.animal_name,
                    birth_year=body.birth_year,
                    species=body.species,
                    gender=body.gender,
                    size=body.size,
                    sterilized=body.sterilized,
                    vaccinated=body.vaccinated,
                    picture=body.picture,
                    race=body.race,
                    special_care=body.special_care,
                    state=body.state,
                    description=body.description,
                ),
            )
        )

    async def get(self, entity_id: str) -> AdoptionAnimalView:
        get_adoption_animal_use_case: GetAdoptionAnimalUseCase = (
            self.dependencies.resolve(GetAdoptionAnimalUseCase)
        )

        return await get_adoption_animal_use_case.execute(entity_id)

    async def index_adoption_animals(
        self,
        species: list[AnimalSpecies] | None = Query(None),
        limit: int | None = None,
        offset: int | None = 0,
    ) -> AdoptionAnimalListView:
        get_adoption_animals_use_case: GetAdoptionAnimalsUseCase = (
            self.dependencies.resolve(GetAdoptionAnimalsUseCase)
        )

        # If FE requests ALL animals, it means we only want to see the animals up for adoption

        return await get_adoption_animals_use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                species=species,
                limit=limit,
                offset=offset,
                state=AdoptionAnimalStates.FOR_ADOPTION,
            )
        )

    async def index_own_adoption_animals(
        self,
        token: TokenDependency,
        species: list[AnimalSpecies] | None = Query(None),
        limit: int | None = None,
        offset: int | None = 0,
    ) -> AdoptionAnimalListView:
        token_data: TokenData = await self._get_token_data(token=token)
        get_adoption_animals_use_case: GetAdoptionAnimalsUseCase = (
            self.dependencies.resolve(GetAdoptionAnimalsUseCase)
        )

        return await get_adoption_animals_use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                species=species,
                limit=limit,
                offset=offset,
                account_id=token_data.account_id,
            )
        )

    async def delete(self, token: TokenDependency, entity_id: str) -> None:
        token_data: TokenData = await self._get_token_data(token=token)
        delete_adoption_animal_use_case: DeleteAdoptionAnimalUseCase = (
            self.dependencies.resolve(DeleteAdoptionAnimalUseCase)
        )
        await delete_adoption_animal_use_case.execute(
            DeleteAdoptionAnimalUseCase.Request(
                entity_id=entity_id, actor_account_id=token_data.account_id
            )
        )

    def register_routes(self) -> None:
        PREFIX: str = "/adoptions/animal_adoption"

        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_put_route(f"{PREFIX}", method=self.put)
        self._register_get_route(f"{PREFIX}", method=self.get)
        self._register_get_route(f"{PREFIX}/all", method=self.index_adoption_animals)
        self._register_get_route(
            f"{PREFIX}/all_own", method=self.index_own_adoption_animals
        )
        self._register_delete_route(f"{PREFIX}", method=self.delete)
