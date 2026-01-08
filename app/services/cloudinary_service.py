from io import BytesIO
from pathlib import Path
from uuid import uuid4
import os

async def upload_to_cloudinary(
    file_bytes: bytes,
    filename: str,
    resource_type: str
) -> str:
    try:
        # Lazy import to avoid hard failure when package missing
        import cloudinary
        import cloudinary.uploader

        # Configure if env available
        cloudinary_url = os.environ.get("CLOUDINARY_URL")
        if cloudinary_url:
            cloudinary.config(cloudinary_url=cloudinary_url)
        else:
            cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
            api_key = os.environ.get("CLOUDINARY_API_KEY")
            api_secret = os.environ.get("CLOUDINARY_API_SECRET")
            if cloud_name and api_key and api_secret:
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret
                )
            else:
                raise Exception("Cloudinary not configured")

        result = cloudinary.uploader.upload(
            BytesIO(file_bytes),
            filename=filename,
            resource_type=resource_type
        )
        return result["secure_url"]
    except Exception:
        root = Path(__file__).resolve().parents[2]
        uploads = root / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        ext = Path(filename).suffix
        unique = f"{uuid4().hex}{ext}"
        path = uploads / unique
        with open(path, "wb") as f:
            f.write(file_bytes)
        return f"/uploads/{unique}"
