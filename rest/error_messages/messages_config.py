from dataclasses import dataclass
from typing import Type

import yaml
from yaml.loader import SafeLoader
from os.path import join as join_path


@dataclass
class AuthMessage:
    email_already_registered: str
    incorrect_login_data: str
    account_not_found: str
    account_not_found_by_email: str
    account_not_found_by_id: str
    account_not_verified: str
    invalid_data_token: str
    decode_token: str
    not_generated_token: str
    unexpected_token: str
    account_already_verified_exception: str


def parse_auth_messages(yaml_data: dict) -> AuthMessage:
    return AuthMessage(
        email_already_registered=yaml_data["auth"]["email_already_registered"],
        incorrect_login_data=yaml_data["auth"]["incorrect_login_data"],
        account_not_found=yaml_data["auth"]["account_not_found"],
        account_not_found_by_email=yaml_data["auth"]["account_not_found_by_email"],
        account_not_found_by_id=yaml_data["auth"]["account_not_found_by_id"],
        account_not_verified=yaml_data["auth"]["account_not_verified"],
        invalid_data_token=yaml_data["auth"]["invalid_data_token"],
        decode_token=yaml_data["auth"]["decode_token"],
        not_generated_token=yaml_data["auth"]["not_generated_token"],
        unexpected_token=yaml_data["auth"]["unexpected_token"],
        account_already_verified_exception=yaml_data["auth"][
            "account_already_verified_exception"
        ],
    )


@dataclass
class SocialMessage:
    organization_already_registered: str
    organization_not_found_by_name: str
    organization_not_found_by_id: str
    profile_already_associated: str
    profile_not_found: str
    personal_profile_not_found: str
    organizational_profile_not_found: str
    view_organizational_profiles: str
    register_organization_admin: str
    accept_organization_member: str
    disable_organization_member: str


def parse_social_messages(yaml_data: dict) -> SocialMessage:
    return SocialMessage(
        organization_already_registered=yaml_data["social"][
            "organization_already_registered"
        ],
        organization_not_found_by_name=yaml_data["social"][
            "organization_not_found_by_name"
        ],
        organization_not_found_by_id=yaml_data["social"][
            "organization_not_found_by_id"
        ],
        profile_already_associated=yaml_data["social"]["profile_already_associated"],
        profile_not_found=yaml_data["social"]["profile_not_found"],
        personal_profile_not_found=yaml_data["social"]["personal_profile_not_found"],
        organizational_profile_not_found=yaml_data["social"][
            "organizational_profile_not_found"
        ],
        view_organizational_profiles=yaml_data["social"][
            "view_organizational_profiles"
        ],
        register_organization_admin=yaml_data["social"]["register_organization_admin"],
        accept_organization_member=yaml_data["social"]["accept_organization_member"],
        disable_organization_member=yaml_data["social"]["disable_organization_member"],
    )


@dataclass
class PetsMessage:
    pet_not_found: str
    owner_is_not_a_personal_profile: str
    pet_already_registered_for_owner: str
    pet_unauthorized_access: str
    sight_for_not_lost_pet: str


def parse_pets_messages(yaml_data: dict) -> PetsMessage:
    return PetsMessage(
        pet_not_found=yaml_data["pets"]["pet_not_found"],
        owner_is_not_a_personal_profile=yaml_data["pets"][
            "owner_is_not_a_personal_profile"
        ],
        pet_already_registered_for_owner=yaml_data["pets"][
            "pet_already_registered_for_owner"
        ],
        pet_unauthorized_access=yaml_data["pets"]["pet_unauthorized_access"],
        sight_for_not_lost_pet=yaml_data["pets"]["sight_for_not_lost_pet"],
    )


@dataclass
class AdoptionsMessage:
    adoption_animal_not_found: str
    animal_species_not_valid: str
    adoption_animal_unauthorized_access: str
    adoption_application_not_found: str
    adoption_application_unauthorized_access: str
    application_by_organization_not_valid: str
    adoption_application_for_own_animal: str
    profile_already_applied: str
    adoption_not_found: str
    animal_already_adopted: str


def parse_adoptions_messages(yaml_data: dict) -> AdoptionsMessage:
    return AdoptionsMessage(
        adoption_animal_not_found=yaml_data["adoptions"]["adoption_animal_not_found"],
        animal_species_not_valid=yaml_data["adoptions"]["animal_species_not_valid"],
        adoption_animal_unauthorized_access=yaml_data["adoptions"][
            "adoption_animal_unauthorized_access"
        ],
        adoption_application_not_found=yaml_data["adoptions"][
            "adoption_application_not_found"
        ],
        adoption_application_unauthorized_access=yaml_data["adoptions"][
            "adoption_application_unauthorized_access"
        ],
        application_by_organization_not_valid=yaml_data["adoptions"][
            "application_by_organization_not_valid"
        ],
        adoption_application_for_own_animal=yaml_data["adoptions"][
            "adoption_application_for_own_animal"
        ],
        profile_already_applied=yaml_data["adoptions"]["profile_already_applied"],
        adoption_not_found=yaml_data["adoptions"]["adoption_not_found"],
        animal_already_adopted=yaml_data["adoptions"]["animal_already_adopted"],
    )


@dataclass
class DonationsMessage:
    collaborator_unauthorized_campaign_management: str
    personal_profile_unauthorized_campaign_management: str
    campaign_already_finished: str
    donation_campaign_not_found: str
    money_amount_not_valid: str
    organizational_profile_unauthorized_to_donate: str
    mp_preference_not_generated: str
    mp_transaction_not_approved: str


def parse_donations_messages(yaml_data: dict) -> DonationsMessage:
    return DonationsMessage(
        collaborator_unauthorized_campaign_management=yaml_data["donations"][
            "collaborator_unauthorized_campaign_management"
        ],
        personal_profile_unauthorized_campaign_management=yaml_data["donations"][
            "personal_profile_unauthorized_campaign_management"
        ],
        campaign_already_finished=yaml_data["donations"]["campaign_already_finished"],
        donation_campaign_not_found=yaml_data["donations"][
            "donation_campaign_not_found"
        ],
        money_amount_not_valid=yaml_data["donations"]["money_amount_not_valid"],
        organizational_profile_unauthorized_to_donate=yaml_data["donations"][
            "organizational_profile_unauthorized_to_donate"
        ],
        mp_preference_not_generated=yaml_data["donations"][
            "mp_preference_not_generated"
        ],
        mp_transaction_not_approved=yaml_data["donations"][
            "mp_transaction_not_approved"
        ],
    )


def get_file_name() -> str:
    return "error_messages.yaml"


def parse_config(file_name: str) -> dict:
    loader: Type[SafeLoader] = yaml.SafeLoader

    with open(join_path("rest", "error_messages", file_name)) as conf_data:
        return yaml.load(conf_data, Loader=loader)


def get_auth_messages() -> AuthMessage:
    auth_messages_dict: dict = parse_config(get_file_name())
    return parse_auth_messages(auth_messages_dict)


def get_social_messages() -> SocialMessage:
    social_messages_dict: dict = parse_config(get_file_name())
    return parse_social_messages(social_messages_dict)


def get_pets_messages() -> PetsMessage:
    pets_messages_dict: dict = parse_config(get_file_name())
    return parse_pets_messages(pets_messages_dict)


def get_adoptions_messages() -> AdoptionsMessage:
    adoptions_messages_dict: dict = parse_config(get_file_name())
    return parse_adoptions_messages(adoptions_messages_dict)


def get_donations_messages() -> DonationsMessage:
    donations_messages_dict: dict = parse_config(get_file_name())
    return parse_donations_messages(donations_messages_dict)


class MessagesConfig:
    def __init__(self) -> None:
        self.auth_messages: AuthMessage = get_auth_messages()
        self.social_messages: SocialMessage = get_social_messages()
        self.pets_messages: PetsMessage = get_pets_messages()
        self.adoptions_messages: AdoptionsMessage = get_adoptions_messages()
        self.donations_messages: DonationsMessage = get_donations_messages()
