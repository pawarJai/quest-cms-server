import cloudinary
import cloudinary.uploader
from io import BytesIO
from pathlib import Path
from uuid import uuid4

async def upload_to_cloudinary(
    file_bytes: bytes,
    filename: str,
    resource_type: str
) -> str:
    try:
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
