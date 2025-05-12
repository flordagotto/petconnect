import io
from abc import ABC, abstractmethod
import qrcode
from qrcode.main import QRCode

from common.background import run_async


class QRCodeGenerator(ABC):
    @abstractmethod
    async def generate_qr_code(self, data: str) -> bytes:
        pass


class PyQRGenerator(QRCodeGenerator):
    # QR code generator using python's qrcode library
    async def generate_qr_code(self, data: str) -> bytes:
        def _generate_qr_code() -> bytes:
            img_byte_arr = io.BytesIO()

            qr = QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            image = qr.make_image(fill_color="black", back_color="white")
            image.save(img_byte_arr, "png")

            return img_byte_arr.getvalue()

        return await run_async(_generate_qr_code)
