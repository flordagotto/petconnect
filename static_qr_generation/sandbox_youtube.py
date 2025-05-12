import io
from uuid import uuid4
from PIL import Image
import qrcode

pet_id = uuid4().hex

# Load your QR code image
img_byte_arr = io.BytesIO()

qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=5, border=1
)

qr.add_data("youtu.be/watch?v=yUQehn2Zkwo")

qr.make(fit=True)

qr_image = qr.make_image(fill_color="black", back_color="white")
qr_image = qr_image.convert("RGB")  # Convert to RGB color mode

# Load your logo image
logo = Image.open(
    "./assets/logo_app.png"
)  # Replace "your_logo.png" with the path to your PNG logo
qr_width, qr_height = qr_image.size

logo = logo.resize((qr_width // 3, qr_height // 3))
logo = logo.convert("RGBA")

# Calculate the position to place the logo in the center of the QR code
qr_width, qr_height = qr_image.size
logo_width, logo_height = logo.size
position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)

# Create a new image with the QR code and logo
final_image = qr_image.copy()
final_image.paste(logo, position)

# Save the final image
final_image.save(f"./static_qr_generation/youtube_video.png", "png")
