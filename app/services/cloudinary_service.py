from io import BytesIO
from pathlib import Path
from uuid import uuid4
import os
import mimetypes
from typing import Optional

async def upload_to_cloudinary(
    file_bytes: bytes,
    filename: str,
    resource_type: str,
    key_prefix: str | None = None
) -> str:
    require_s3 = os.environ.get("AWS_S3_REQUIRED", "").lower() in ("1", "true", "yes")
    bucket = os.environ.get("AWS_S3_BUCKET")
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if bucket and access_key and secret_key:
        try:
            import boto3
            from botocore.config import Config
            connect_timeout = int(os.environ.get("AWS_S3_CONNECT_TIMEOUT", "5"))
            read_timeout = int(os.environ.get("AWS_S3_READ_TIMEOUT", "20"))
            max_attempts = int(os.environ.get("AWS_S3_MAX_ATTEMPTS", "2"))
            cfg = Config(connect_timeout=connect_timeout, read_timeout=read_timeout, retries={"max_attempts": max_attempts, "mode": "standard"})
            s3 = boto3.client(
                "s3",
                region_name=os.environ.get("AWS_S3_REGION"),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=cfg,
            )
            ext = Path(filename).suffix
            default_prefix = None
            if not key_prefix:
                if resource_type == "image":
                    default_prefix = os.environ.get("AWS_S3_IMAGE_PREFIX", "images")
                elif resource_type == "video":
                    default_prefix = os.environ.get("AWS_S3_VIDEO_PREFIX", "videos")
                elif resource_type == "raw":
                    default_prefix = os.environ.get("AWS_S3_DOC_PREFIX", "docs")
            prefix = key_prefix or default_prefix
            if prefix:
                key = f"{prefix.rstrip('/')}/{uuid4().hex}{ext}"
            else:
                key = f"{uuid4().hex}{ext}"
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
            force_presigned = os.environ.get("AWS_S3_FORCE_PRESIGNED", "").lower() in ("1", "true", "yes")
            if force_presigned:
                presigned = s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": bucket, "Key": key},
                    ExpiresIn=int(os.environ.get("AWS_S3_PRESIGNED_SECONDS", "3600")),
                )
                return presigned
            base_url = os.environ.get("AWS_S3_PUBLIC_BASE_URL")
            if base_url:
                return f"{base_url.rstrip('/')}/{key}"
            region = os.environ.get("AWS_S3_REGION")
            if region:
                return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
            return f"https://{bucket}.s3.amazonaws.com/{key}"
        except Exception:
            if require_s3:
                raise
            pass
    elif require_s3:
        raise Exception("S3 required but not configured")
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
        if require_s3:
            raise
        uploads_dir_str = os.environ.get("UPLOADS_DIR")
        if uploads_dir_str:
            uploads = Path(uploads_dir_str)
        else:
            root = Path(__file__).resolve().parents[2]
            uploads = root / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        ext = Path(filename).suffix
        unique = f"{uuid4().hex}{ext}"
        path = uploads / unique
        with open(path, "wb") as f:
            f.write(file_bytes)
        return f"/uploads/{unique}"
