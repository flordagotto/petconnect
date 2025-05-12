from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Sequence
from uuid import uuid4

from bounded_contexts.adoptions_domain.entities import (
    AdoptionAnimal,
    AdoptionApplication,
)
from bounded_contexts.adoptions_domain.entities.adoption import Adoption
from bounded_contexts.adoptions_domain.enum import (
    AdoptionAnimalStates,
    HousingTypes,
    OpenSpacesTypes,
    AdoptionApplicationStates,
)
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    AdoptionApplicationService,
    AdoptionApplicationData,
)
from bounded_contexts.adoptions_domain.services.adoption_service import (
    AdoptionData,
    AdoptionService,
)
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
)
from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.donations_domain.entities import DonationCampaign
from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
    CreateDonationCampaignData,
)
from bounded_contexts.pets_domain.entities import Pet, PetSight
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.services import (
    PetService,
    PetData,
    PetSightService,
)
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    Organization,
    OrganizationalProfile,
    PersonalProfile,
)
from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import (
    CreatePersonalProfileUseCase,
    CreateOrganizationUseCase,
)
from common.dependencies import DependencyContainer
from config import ProjectConfig
from infrastructure.date_utils import (
    date_now,
    datetime_now_tz,
)
from infrastructure.payment_gateway import MerchantData
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class ProfileData:
    profile_id: str
    account_id: str
    email: str


@dataclass
class PersonalProfileData:
    entity_id: str
    first_name: str
    surname: str
    phone_number: str
    government_id: str
    birth_date: date
    social_media_url: str | None = None


@dataclass
class OrganizationalProfileData:
    profile_data: ProfileData
    organization: Organization


@dataclass
class PetDataForTesting:
    pet_data: PetData
    profile_id: str


@dataclass
class AdoptionAnimalDataForTesting:
    adoption_animal_data: AdoptionAnimalData
    profile_id: str


@dataclass
class AdoptionApplicationDataForTesting:
    adoption_application_data: AdoptionApplicationData
    profile_id: str


@dataclass
class DonationCampaignDataForTesting:
    entity_id: str
    organization_id: str
    donation_campaign_data: DonationCampaign


class BaseTestingUtils(ABC):
    async def create_profile(
        self, uow: UnitOfWork, email: str | None = None
    ) -> ProfileData:
        request: CreatePersonalProfileUseCase.Request = (
            CreatePersonalProfileUseCase.Request(
                account_request=CreateAccountUseCase.Request(
                    email=email if email is not None else f"{uuid4().hex}@hotmail.com",
                    password="test_password",
                ),
                first_name="gaspar",
                surname="noriega",
                phone_number="3512421500",
                birthdate=date_now(),
                government_id="40123123",
            )
        )

        account: Account = await self.accounts_service.create_account(
            uow=uow,
            email=request.account_request.email,
            password=request.account_request.password,
        )

        profile: BaseProfile = await self.profile_service.create_personal_profile(
            uow=uow,
            account=await self.accounts_service.get_account_by_id(
                uow=uow, account_id=account.entity_id
            ),
            first_name=request.first_name,
            surname=request.surname,
            phone_number=request.phone_number,
            birthdate=date_now(),
            government_id="40123123",
        )

        return ProfileData(
            profile_id=profile.entity_id,
            account_id=account.entity_id,
            email=account.email,
        )

    async def get_personal_profile(
        self, uow: UnitOfWork, profile_id: str
    ) -> PersonalProfileData:
        profile: PersonalProfile = await self.profile_service.get_personal_profile(
            uow=uow, entity_id=profile_id
        )

        return PersonalProfileData(
            entity_id=profile.entity_id,
            first_name=profile.first_name,
            surname=profile.surname,
            phone_number=profile.phone_number,
            government_id=profile.government_id,
            birth_date=profile.birthdate,
            social_media_url=profile.social_media_url,
        )

    async def create_organizational_profile(
        self,
        uow: UnitOfWork,
        account_email: str = "gasparnoriega@hotmail.com",
        organization_name: str = "patitas del sur",
        verified_bank: bool = True,
    ) -> OrganizationalProfileData:
        request: CreateOrganizationUseCase.Request = CreateOrganizationUseCase.Request(
            organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                email=account_email,
                password="test_password",
                first_name="gaspar",
                surname="noriega",
                phone_number="3512421500",
                government_id="1234",
                birthdate=date_now(),
            ),
            organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                organization_name=organization_name, phone_number="3512421500"
            ),
        )

        account: Account = await self.accounts_service.create_account(
            uow=uow,
            email=request.organization_admin_request.email,
            password=request.organization_admin_request.password,
        )

        organization: Organization = (
            await self.organization_service.create_organization(
                uow=uow,
                organization_name=request.organization_request.organization_name,
                creator_account_id=account.entity_id,
                phone_number=request.organization_request.phone_number,
            )
        )

        organizational_profile: OrganizationalProfile = (
            await self.profile_service.create_organization_admin_profile(
                uow=uow,
                account=await self.accounts_service.get_account_by_id(
                    uow=uow, account_id=account.entity_id
                ),
                first_name=request.organization_admin_request.first_name,
                surname=request.organization_admin_request.surname,
                phone_number=request.organization_admin_request.phone_number,
                government_id=request.organization_admin_request.government_id,
                organization_id=organization.entity_id,
                birthdate=date_now(),
            )
        )

        profile_data: ProfileData = ProfileData(
            profile_id=organizational_profile.entity_id,
            account_id=account.entity_id,
            email=account.email,
        )

        if verified_bank:
            organization.verified_bank = True

            organization.merchant_data = MerchantData(
                access_token="test_access_token",
                token_type="test_token_type",
                expires_in=1000,
                scope="test_scope",
                user_id=1,
                refresh_token="test_refresh_token",
                public_key="test_public_key",
            )

        return OrganizationalProfileData(
            profile_data=profile_data, organization=organization
        )

    async def create_organizational_collaborator_profile(
        self,
        uow: UnitOfWork,
        organization_id: str,
        account_email: str = "gasparnoriega@hotmail.com",
    ) -> OrganizationalProfileData:
        organization: Organization = (
            await self.organization_service.get_organization_by_id(
                uow=uow, entity_id=organization_id
            )
        )

        account: Account = await self.accounts_service.create_account(
            uow=uow,
            email=account_email,
            password="test_password",
        )

        organizational_profile: OrganizationalProfile = (
            await self.profile_service.create_organization_employee_profile(
                uow=uow,
                account=await self.accounts_service.get_account_by_id(
                    uow=uow, account_id=account.entity_id
                ),
                first_name="gaspar",
                surname="noriega",
                phone_number="3512421500",
                government_id="1234",
                birthdate=date_now(),
                organization_id=organization.entity_id,
                organization_role=OrganizationRoles.COLLABORATOR,
            )
        )

        profile_data: ProfileData = ProfileData(
            profile_id=organizational_profile.entity_id,
            account_id=account.entity_id,
            email=account.email,
        )

        return OrganizationalProfileData(
            profile_data=profile_data, organization=organization
        )

    async def create_organization(
        self,
        uow: UnitOfWork,
        account_email: str = "gasparnoriega@hotmail.com",
        organization_name: str = "patitas del sur",
    ) -> Organization:
        await self.create_organizational_profile(
            uow=uow, account_email=account_email, organization_name=organization_name
        )

        return await self.organization_service.get_organization_by_name(
            uow=uow, organization_name=organization_name
        )

    async def create_pet(
        self,
        uow: UnitOfWork,
        actor_profile: ProfileData,
        pet_data: PetData | None = None,
        lost: bool = False,
    ) -> PetDataForTesting:
        if pet_data is None:
            pet_data = PetData(
                entity_id="",
                animal_name="Pepito",
                birth_year=2023,
                species=AnimalSpecies.OTHER,
                gender=AnimalGender.MALE,
                size=AnimalSize.BIG,
                sterilized=True,
                vaccinated=True,
                lost=lost,
                qr_code="https://.../qr/id_pepito",
                picture="https://.../picture/id_pepito",
                race="siames",
                special_care="medicacion",
            )

        pet: Pet = await self.pet_service.create_pet(
            uow=uow,
            actor_profile=await self.profile_service.get_profile(
                uow=uow, entity_id=actor_profile.profile_id
            ),
            animal_name=pet_data.animal_name,
            birth_year=pet_data.birth_year,
            species=pet_data.species,
            gender=pet_data.gender,
            size=pet_data.size,
            sterilized=pet_data.sterilized,
            vaccinated=pet_data.vaccinated,
            lost=pet_data.lost,
            picture=pet_data.picture,
            race=pet_data.race,
            special_care=pet_data.special_care,
        )

        pet_data.entity_id = pet.entity_id
        pet_data.qr_code = pet.qr_code

        return PetDataForTesting(pet_data=pet_data, profile_id=actor_profile.profile_id)

    async def get_pet(self, uow: UnitOfWork, pet_id: str) -> PetData:
        pet: Pet = await self.pet_service.get_pet_by_id(uow=uow, entity_id=pet_id)

        return PetData(
            entity_id=pet.entity_id,
            animal_name=pet.animal_name,
            birth_year=pet.birth_year,
            species=pet.species,
            gender=pet.gender,
            size=pet.size,
            sterilized=pet.sterilized,
            vaccinated=pet.vaccinated,
            lost=pet.lost,
            lost_date=pet.lost_date,
            qr_code=pet.qr_code,
            picture=pet.picture,
            race=pet.race,
            special_care=pet.special_care,
        )

    async def create_pet_sight(
        self, uow: UnitOfWork, pet_id: str, account_id: str
    ) -> PetSight:
        pet: Pet = await self.pet_service.get_pet_by_id(uow=uow, entity_id=pet_id)

        return await self.pet_sight_service.create_pet_sight(
            uow=uow,
            pet=pet,
            latitude=11552214.10,
            longitude=22663325.25,
            account_id=account_id,
        )

    async def get_pet_sights_by_pet_id(
        self, uow: UnitOfWork, pet_id: str
    ) -> Sequence[PetSight]:
        pet_sights: Sequence[
            PetSight
        ] = await self.pet_sight_service.get_all_pet_sights(uow=uow, pet_id=pet_id)

        return pet_sights

    async def create_adoption_animal(
        self,
        uow: UnitOfWork,
        actor_profile: ProfileData,
        adoption_animal_data: AdoptionAnimalData | None = None,
    ) -> AdoptionAnimalDataForTesting:
        if adoption_animal_data is None:
            adoption_animal_data = AdoptionAnimalData(
                entity_id="",
                animal_name="Pepito",
                birth_year=2023,
                species=AnimalSpecies.OTHER,
                gender=AnimalGender.MALE,
                size=AnimalSize.BIG,
                sterilized=True,
                vaccinated=True,
                picture="https://.../picture/id_pepito",
                state=AdoptionAnimalStates.FOR_ADOPTION,
                race="siames",
                special_care="medicacion",
            )

        adoption_animal: AdoptionAnimal = (
            await self.adoption_animal_service.create_adoption_animal(
                uow=uow,
                actor_profile=await self.profile_service.get_profile(
                    uow=uow, entity_id=actor_profile.profile_id
                ),
                animal_name=adoption_animal_data.animal_name,
                birth_year=adoption_animal_data.birth_year,
                species=adoption_animal_data.species,
                gender=adoption_animal_data.gender,
                size=adoption_animal_data.size,
                sterilized=adoption_animal_data.sterilized,
                vaccinated=adoption_animal_data.vaccinated,
                picture=adoption_animal_data.picture,
                state=adoption_animal_data.state,
                race=adoption_animal_data.race,
                special_care=adoption_animal_data.special_care,
                description=adoption_animal_data.description,
                publication_date=adoption_animal_data.publication_date,
            )
        )

        adoption_animal_data.entity_id = adoption_animal.entity_id

        return AdoptionAnimalDataForTesting(
            adoption_animal_data=adoption_animal_data,
            profile_id=actor_profile.profile_id,
        )

    async def get_all_adoption_animal(
        self, uow: UnitOfWork, adoption_animal_id: str
    ) -> AdoptionAnimalData:
        adoption_animal: AdoptionAnimal = (
            await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow, entity_id=adoption_animal_id, get_all=True
            )
        )

        return AdoptionAnimalData(
            entity_id=adoption_animal.entity_id,
            animal_name=adoption_animal.animal_name,
            birth_year=adoption_animal.birth_year,
            species=adoption_animal.species,
            gender=adoption_animal.gender,
            size=adoption_animal.size,
            sterilized=adoption_animal.sterilized,
            vaccinated=adoption_animal.vaccinated,
            picture=adoption_animal.picture,
            state=adoption_animal.state,
            race=adoption_animal.race,
            special_care=adoption_animal.special_care,
            description=adoption_animal.description,
            deleted=adoption_animal.deleted,
            publication_date=adoption_animal.publication_date,
        )

    async def create_adoption_application(
        self,
        uow: UnitOfWork,
        actor_profile: ProfileData,
        animal_id: str,
        adoption_application_data: AdoptionApplicationData | None = None,
    ) -> AdoptionApplicationDataForTesting:
        animal: AdoptionAnimal = (
            await self.adoption_animal_service.get_adoption_animal_by_id(
                uow=uow, entity_id=animal_id
            )
        )

        if adoption_application_data is None:
            adoption_application_data = AdoptionApplicationData(
                entity_id="",
                ever_had_pet=False,
                has_pet=True,
                type_of_housing=HousingTypes.HOUSE,
                open_space=OpenSpacesTypes.BALCONY,
                pet_time_commitment="tengo mucho tiempo",
                adoption_info="quiero una mascota",
                adopter_profile_id=actor_profile.profile_id,
                animal_id=animal_id,
                application_date=datetime_now_tz(),
                safety_in_open_spaces="tengo rejas en el balcon",
                animal_nice_to_others="es un gato amigable",
                state=AdoptionApplicationStates.PENDING,
            )

        application: AdoptionApplication = (
            await self.adoption_application_service.create_application(
                uow=uow,
                animal=animal,
                ever_had_pet=adoption_application_data.ever_had_pet,
                has_pet=adoption_application_data.has_pet,
                type_of_housing=adoption_application_data.type_of_housing,
                open_space=adoption_application_data.open_space,
                pet_time_commitment=adoption_application_data.pet_time_commitment,
                adoption_info=adoption_application_data.adoption_info,
                adopter_profile=await self.profile_service.get_profile(
                    uow=uow, entity_id=adoption_application_data.adopter_profile_id
                ),
                safety_in_open_spaces=adoption_application_data.safety_in_open_spaces,
                animal_nice_to_others=adoption_application_data.animal_nice_to_others,
            )
        )

        adoption_application_data.entity_id = application.entity_id

        return AdoptionApplicationDataForTesting(
            adoption_application_data=adoption_application_data,
            profile_id=actor_profile.profile_id,
        )

    async def get_adoption_application(
        self, uow: UnitOfWork, adoption_application_id: str
    ) -> AdoptionApplicationData:
        adoption_application: AdoptionApplication = (
            await self.adoption_application_service.get_application_by_id(
                uow=uow, entity_id=adoption_application_id
            )
        )

        return AdoptionApplicationData(
            entity_id=adoption_application.entity_id,
            ever_had_pet=adoption_application.ever_had_pet,
            has_pet=adoption_application.has_pet,
            type_of_housing=adoption_application.type_of_housing,
            open_space=adoption_application.open_space,
            pet_time_commitment=adoption_application.pet_time_commitment,
            adoption_info=adoption_application.adoption_info,
            adopter_profile_id=adoption_application.adopter_profile_id,
            animal_id=adoption_application.animal_id,
            state=adoption_application.state,
            application_date=adoption_application.application_date,
            safety_in_open_spaces=adoption_application.safety_in_open_spaces,
            animal_nice_to_others=adoption_application.animal_nice_to_others,
        )

    async def get_adoption(
        self, uow: UnitOfWork, adoption_application_id: str
    ) -> AdoptionData:
        adoption: Adoption = await self.adoption_service.get_adoption_by_application_id(
            uow=uow, adoption_application_id=adoption_application_id
        )

        return AdoptionData(
            entity_id=adoption.entity_id,
            adoption_date=adoption.adoption_date,
            adoption_application_id=adoption.adoption_application_id,
        )

    async def get_adoption_applications_by_animal_id(
        self, uow: UnitOfWork, adoption_animal_id: str
    ) -> Sequence[AdoptionApplicationData]:
        adoption_applications: Sequence[
            AdoptionApplication
        ] = await self.adoption_application_service.get_applications_by_animal_id(
            uow=uow, adoption_animal_id=adoption_animal_id
        )

        adoption_applications_data: list[AdoptionApplicationData] = []

        for application in adoption_applications:
            application_data = AdoptionApplicationData(
                entity_id=application.entity_id,
                ever_had_pet=application.ever_had_pet,
                has_pet=application.has_pet,
                type_of_housing=application.type_of_housing,
                pet_time_commitment=application.pet_time_commitment,
                adoption_info=application.adoption_info,
                adopter_profile_id=application.adopter_profile_id,
                animal_id=application.animal_id,
                application_date=application.application_date,
                open_space=application.open_space,
                safety_in_open_spaces=application.safety_in_open_spaces,
                animal_nice_to_others=application.animal_nice_to_others,
                state=application.state,
            )
            adoption_applications_data.append(application_data)

        return adoption_applications_data

    async def create_donation_campaign(
        self,
        uow: UnitOfWork,
        profile: OrganizationalProfileData,
        donation_campaign_data: CreateDonationCampaignData | None = None,
    ) -> DonationCampaignDataForTesting:
        if donation_campaign_data is None:
            donation_campaign_data = CreateDonationCampaignData(
                campaign_name="Donate for Pepito!",
                campaign_picture="https://petconnect.icu/campaign_picture/id_campaign_pepito.jpg",
                money_goal=2500,
                campaign_description="Donate for Pepito's surgery",
                additional_information="Pepito needs a surgery for his kidney's stones",
            )

        donation_campaign: DonationCampaign = (
            await self.donation_service.create_donation_campaign(
                uow=uow,
                profile=await self.profile_service.get_profile(
                    uow=uow, entity_id=profile.profile_data.profile_id
                ),
                donation_campaign_data=donation_campaign_data,
            )
        )

        return DonationCampaignDataForTesting(
            entity_id=donation_campaign.entity_id,
            organization_id=donation_campaign.organization_id,
            donation_campaign_data=donation_campaign,
        )

    async def get_donation_campaign_by_id(
        self, uow: UnitOfWork, donation_campaign_id: str
    ) -> DonationCampaign:
        return await self.donation_service.get_donation_campaign(
            uow=uow, donation_campaign_id=donation_campaign_id
        )

    async def get_donation_campaigns(
        self, uow: UnitOfWork, active: bool = True, organization_id: str | None = None
    ) -> Sequence[DonationCampaign]:
        donation_campaigns: Sequence[
            DonationCampaign
        ] = await self.donation_service.get_all_donation_campaigns(
            uow=uow, active=active, organization_id=organization_id
        )

        donation_campaigns_data: list[DonationCampaign] = []

        for donation_campaign in donation_campaigns:
            donation_campaign_data = DonationCampaign(
                entity_id=donation_campaign.entity_id,
                organization_id=donation_campaign.organization_id,
                campaign_picture=donation_campaign.campaign_picture,
                campaign_name=donation_campaign.campaign_name,
                money_goal=donation_campaign.money_goal,
                campaign_description=donation_campaign.campaign_description,
                additional_information=donation_campaign.additional_information,
                active=donation_campaign.active,
            )
            donation_campaigns_data.append(donation_campaign_data)

        return donation_campaigns_data

    async def close_campaign(
        self, uow: UnitOfWork, donation_campaign_id: str, profile_id: str
    ) -> None:
        donation_campaign: DonationCampaign = (
            await self.donation_service.get_donation_campaign(
                uow=uow, donation_campaign_id=donation_campaign_id
            )
        )
        profile: BaseProfile = await self.profile_service.get_profile(
            uow=uow, entity_id=profile_id
        )

        await self.donation_service.close_campaign(
            uow=uow, profile=profile, donation_campaign=donation_campaign
        )

    @property
    def project_config(self) -> ProjectConfig:
        return self.get_dependencies().resolve(ProjectConfig)

    @property
    def accounts_service(self) -> AccountsService:
        return self.get_dependencies().resolve(AccountsService)

    @property
    def profile_service(self) -> ProfileService:
        return self.get_dependencies().resolve(ProfileService)

    @property
    def organization_service(self) -> OrganizationService:
        return self.get_dependencies().resolve(OrganizationService)

    @property
    def pet_service(self) -> PetService:
        return self.get_dependencies().resolve(PetService)

    @property
    def pet_sight_service(self) -> PetSightService:
        return self.get_dependencies().resolve(PetSightService)

    @property
    def adoption_animal_service(self) -> AdoptionAnimalsService:
        return self.get_dependencies().resolve(AdoptionAnimalsService)

    @property
    def adoption_application_service(self) -> AdoptionApplicationService:
        return self.get_dependencies().resolve(AdoptionApplicationService)

    @property
    def adoption_service(self) -> AdoptionService:
        return self.get_dependencies().resolve(AdoptionService)

    @property
    def donation_service(self) -> DonationsService:
        return self.get_dependencies().resolve(DonationsService)

    @abstractmethod
    def get_dependencies(self) -> DependencyContainer:
        pass
