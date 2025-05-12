from enum import Enum
from uuid import uuid4
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from infrastructure.file_system import FileSystemPrefix, Boto3S3FileSystemGateway
from infrastructure.rest import BaseAPIController


class PresignedUrlResponse(BaseModel):
    url: str
    fields: dict


class ImageExtensions(Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


class FilesController(BaseAPIController):
    class GeneratePresignedUrl(BaseModel):
        prefix: FileSystemPrefix
        extension: ImageExtensions

    async def post(self, body: GeneratePresignedUrl) -> PresignedUrlResponse:
        file_gateway = self.dependencies.resolve(Boto3S3FileSystemGateway)

        presigned_url = await file_gateway.generate_presigned_post_url(
            prefix=body.prefix, file_key=uuid4().hex + "." + body.extension.value
        )

        return PresignedUrlResponse(
            url=presigned_url["url"], fields=presigned_url["fields"]
        )

    async def get(self, prefix: FileSystemPrefix, file_key: str) -> RedirectResponse:
        file_gateway = self.dependencies.resolve(Boto3S3FileSystemGateway)

        url = await file_gateway.generate_presigned_get_url(
            prefix=prefix, file_key=file_key
        )

        return RedirectResponse(url)

    def register_routes(self) -> None:
        PREFIX: str = "/files/"

        self._register_post_route(f"{PREFIX}generate_presigned_url", method=self.post)
        self._register_redirect_route(
            f"{PREFIX}" + "{prefix}/{file_key}",
            method=self.get,
            response_class=RedirectResponse,
        )
