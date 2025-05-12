from abc import ABC, abstractmethod
from enum import Enum
import boto3
from botocore.config import Config

from common.background import run_async


class FileSystemPrefix(Enum):
    QR = "QR"
    PET = "PET"


class FileSystemGateway(ABC):
    @abstractmethod
    async def save_file(
        self, prefix: FileSystemPrefix, file_key: str, file: bytes
    ) -> None:
        pass

    @abstractmethod
    async def get_file(self, prefix: FileSystemPrefix, file_key: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, prefix: FileSystemPrefix, file_key: str) -> None:
        pass


class TestingFileSystemGateway(FileSystemGateway):
    async def save_file(
        self, prefix: FileSystemPrefix, file_key: str, file: bytes
    ) -> None:
        def _save_file() -> None:
            print("Saving file...")

        await run_async(_save_file)

    async def get_file(self, prefix: FileSystemPrefix, file_key: str) -> bytes:
        def _get_file() -> bytes:
            return bytes()

        return await run_async(_get_file)

    async def delete_file(self, prefix: FileSystemPrefix, file_key: str) -> None:
        def _delete_file() -> None:
            print("Deleting file...")

        await run_async(_delete_file)


class Boto3S3FileSystemGateway(FileSystemGateway):
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ) -> None:
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            region_name="us-east-2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(signature_version="s3v4"),
        )

    async def save_file(
        self, prefix: FileSystemPrefix, file_key: str, file: bytes
    ) -> None:
        def _save_file():
            file_path = prefix.value + "/" + file_key

            self.s3.put_object(Bucket=self.bucket_name, Key=file_path, Body=file)

        await run_async(_save_file)

    async def get_file(self, prefix: FileSystemPrefix, file_key: str) -> bytes:
        def _get_file() -> bytes:
            file_path = prefix.value + "/" + file_key

            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_path)
            return response["Body"].read()

        return await run_async(_get_file)

    async def delete_file(self, prefix: FileSystemPrefix, file_key: str) -> None:
        def _delete_file():
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)

        await run_async(_delete_file)

    async def generate_presigned_post_url(
        self, prefix: FileSystemPrefix, file_key: str
    ) -> dict:
        def _create_presigned_url() -> str:
            file_path = prefix.value + "/" + file_key

            content_type = f"image/{file_key.split('.')[-1]}"

            response = self.s3.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=file_path,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                ],
                ExpiresIn=3600,
            )

            return response

        return await run_async(_create_presigned_url)

    async def generate_presigned_get_url(
        self, prefix: FileSystemPrefix, file_key: str
    ) -> str:
        def _create_presigned_url() -> str:
            file_path = prefix.value + "/" + file_key

            response = self.s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": file_path,
                    "ResponseContentType": f'image/{file_key.split(".")[-1]}',
                },
                ExpiresIn=3600,
            )

            return response

        return await run_async(_create_presigned_url)
