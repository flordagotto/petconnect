import os
import re
from dataclasses import dataclass
from enum import Enum
from re import Pattern
from typing import Type

import yaml
from yaml.loader import SafeLoader
from os.path import join as join_path


@dataclass
class UrlConfig:
    backend_url: str
    frontend_url: str


@dataclass
class S3Config:
    fake: bool
    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str


@dataclass
class CryptoConfig:
    token_secret: str
    algorithm: str


@dataclass
class DBPoolConfig:
    max_overflow: int
    size: int
    recycle: int
    timeout: int


@dataclass
class DBConnectionConfig:
    user: str
    password: str
    host: str
    db_name: str
    port: int


@dataclass
class DatabaseConfig:
    db: str
    echo: bool
    pool: DBPoolConfig
    connection: DBConnectionConfig


@dataclass
class EmailConfig:
    email_environment: str
    sendgrid_api_key: str
    sendgrid_from_email: str


@dataclass
class MercadoPagoConfig:
    access_token: str
    client_id: str
    client_secret: str


@dataclass
class StaffConfig:
    staff_email: str


def parse_s3_config(yaml_data: dict) -> S3Config:
    return S3Config(
        fake=yaml_data["s3_config"]["fake"],
        bucket_name=yaml_data["s3_config"]["bucket_name"],
        aws_access_key_id=yaml_data["s3_config"]["aws_access_key_id"],
        aws_secret_access_key=yaml_data["s3_config"]["aws_secret_access_key"],
    )


def parse_url_config(yaml_data: dict) -> UrlConfig:
    return UrlConfig(
        backend_url=yaml_data["url_config"]["backend_url"],
        frontend_url=yaml_data["url_config"]["frontend_url"],
    )


def parse_crypto_config(yaml_data: dict) -> CryptoConfig:
    return CryptoConfig(
        token_secret=yaml_data["crypto"]["token_secret"],
        algorithm=yaml_data["crypto"]["algorithm"],
    )


def parse_database_config(yaml_data: dict) -> DatabaseConfig:
    return DatabaseConfig(
        db=yaml_data["database"]["db"],
        echo=yaml_data["database"]["echo"],
        pool=DBPoolConfig(
            max_overflow=yaml_data["database"]["pool"]["max_overflow"],
            size=yaml_data["database"]["pool"]["size"],
            recycle=yaml_data["database"]["pool"]["recycle_sec"],
            timeout=yaml_data["database"]["pool"]["timeout_sec"],
        ),
        connection=DBConnectionConfig(
            user=yaml_data["database"]["connection"]["user"],
            password=yaml_data["database"]["connection"]["password"],
            host=yaml_data["database"]["connection"]["host"],
            db_name=yaml_data["database"]["connection"]["db_name"],
            port=yaml_data["database"]["connection"]["port"],
        ),
    )


def parse_email_config(yaml_data: dict) -> EmailConfig:
    return EmailConfig(
        email_environment=yaml_data["email"]["email_environment"],
        sendgrid_api_key=yaml_data["email"]["sendgrid_api_key"],
        sendgrid_from_email=yaml_data["email"]["sendgrid_from_email"],
    )


def parse_mp_config(yaml_data: dict) -> MercadoPagoConfig:
    return MercadoPagoConfig(
        access_token=yaml_data["mp_config"]["access_token"],
        client_id=yaml_data["mp_config"]["client_id"],
        client_secret=yaml_data["mp_config"]["client_secret"],
    )


def parse_staff_config(yaml_data: dict) -> StaffConfig:
    return StaffConfig(
        staff_email=yaml_data["staff_config"]["staff_email"],
    )


class YamlConfigFileName(Enum):
    APP_CONFIG = "app_config.yaml"
    TESTING = "testing_config.yaml"


def parse_config(file_name: str) -> dict:
    tag: str = "!ENV"
    pattern: Pattern = re.compile(".*?\${(\w+)}.*?")
    loader: Type[SafeLoader] = yaml.SafeLoader
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(yaml_loader, node):
        value = yaml_loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(f"${{{g}}}", os.environ.get(g, g))
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    with open(join_path(absolute_path, file_name)) as conf_data:
        return yaml.load(conf_data, Loader=loader)


def get_crypto_config(config_file_name: YamlConfigFileName) -> CryptoConfig:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_crypto_config(config_dict)


def get_database_config(config_file_name: YamlConfigFileName) -> DatabaseConfig:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_database_config(config_dict)


def get_email_config(config_file_name: YamlConfigFileName) -> EmailConfig:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_email_config(config_dict)


def get_url_config(config_file_name: YamlConfigFileName) -> UrlConfig:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_url_config(config_dict)


def get_s3_config(config_file_name: YamlConfigFileName) -> S3Config:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_s3_config(config_dict)


def get_mp_config(config_file_name: YamlConfigFileName) -> MercadoPagoConfig:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_mp_config(config_dict)


def get_staff_config(config_file_name: YamlConfigFileName) -> StaffConfig:
    config_dict: dict = parse_config(config_file_name.value)
    return parse_staff_config(config_dict)


class ProjectConfig:
    def __init__(
        self,
        config_file_name: YamlConfigFileName,
    ) -> None:
        self.config_file_name: YamlConfigFileName = config_file_name
        self.crypto: CryptoConfig = get_crypto_config(config_file_name)
        self.database: DatabaseConfig = get_database_config(config_file_name)
        self.email: EmailConfig = get_email_config(config_file_name)
        self.url_config: UrlConfig = get_url_config(config_file_name)
        self.s3_config: S3Config = get_s3_config(config_file_name)
        self.mp_config: MercadoPagoConfig = get_mp_config(config_file_name)
        self.staff_config: StaffConfig = get_staff_config(config_file_name)
