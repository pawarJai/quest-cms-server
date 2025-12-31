import cloudinary
import cloudinary.uploader
from io import BytesIO

async def upload_to_cloudinary(
    file_bytes: bytes,
    filename: str,
    resource_type: str
) -> str:
    
    result = cloudinary.uploader.upload(
        BytesIO(file_bytes),
        filename=filename,
        resource_type=resource_type
    )

    return result["secure_url"]
