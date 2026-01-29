import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import uuid
from datetime import datetime
from ..config import settings


class StorageService:
    """Service for managing video storage in Cloudflare R2."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy initialization of S3 client for R2."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.r2_endpoint,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                config=Config(
                    signature_version="s3v4",
                    retries={"max_attempts": 3, "mode": "standard"}
                ),
            )
        return self._client

    def _generate_key(self, session_id: str, question_index: int, extension: str = "webm") -> str:
        """Generate a unique storage key for a video."""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8]
        return f"interviews/{session_id}/{question_index}_{timestamp}_{unique_id}.{extension}"

    async def upload_video(
        self,
        file: BinaryIO,
        session_id: str,
        question_index: int,
        content_type: str = "video/webm",
        extension: str = "webm"
    ) -> str:
        """
        Upload a video file to R2 storage.

        Args:
            file: File-like object containing video data
            session_id: Interview session ID
            question_index: Question number (0-indexed)
            content_type: MIME type of the video
            extension: File extension

        Returns:
            The storage key for the uploaded video
        """
        key = self._generate_key(session_id, question_index, extension)

        try:
            self.client.upload_fileobj(
                file,
                settings.r2_bucket_name,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {
                        "session_id": session_id,
                        "question_index": str(question_index),
                    }
                }
            )
            return key
        except ClientError as e:
            raise Exception(f"Failed to upload video: {e}")

    async def upload_video_bytes(
        self,
        data: bytes,
        session_id: str,
        question_index: int,
        content_type: str = "video/webm",
        extension: str = "webm"
    ) -> str:
        """
        Upload video bytes to R2 storage.

        Args:
            data: Raw video bytes
            session_id: Interview session ID
            question_index: Question number (0-indexed)
            content_type: MIME type of the video
            extension: File extension

        Returns:
            The storage key for the uploaded video
        """
        from io import BytesIO
        file = BytesIO(data)
        return await self.upload_video(file, session_id, question_index, content_type, extension)

    def get_signed_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for accessing a video.

        Args:
            key: Storage key of the video
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL for accessing the video
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.r2_bucket_name,
                    "Key": key,
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate signed URL: {e}")

    def get_upload_url(self, session_id: str, question_index: int, expiration: int = 3600) -> tuple[str, str]:
        """
        Generate a presigned URL for direct upload from client.

        Args:
            session_id: Interview session ID
            question_index: Question number
            expiration: URL expiration time in seconds

        Returns:
            Tuple of (presigned_url, storage_key)
        """
        key = self._generate_key(session_id, question_index)
        try:
            url = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.r2_bucket_name,
                    "Key": key,
                    "ContentType": "video/webm",
                },
                ExpiresIn=expiration
            )
            return url, key
        except ClientError as e:
            raise Exception(f"Failed to generate upload URL: {e}")

    async def delete_video(self, key: str) -> bool:
        """
        Delete a video from R2 storage.

        Args:
            key: Storage key of the video to delete

        Returns:
            True if deletion was successful
        """
        try:
            self.client.delete_object(
                Bucket=settings.r2_bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete video: {e}")

    async def video_exists(self, key: str) -> bool:
        """
        Check if a video exists in storage.

        Args:
            key: Storage key to check

        Returns:
            True if video exists
        """
        try:
            self.client.head_object(
                Bucket=settings.r2_bucket_name,
                Key=key
            )
            return True
        except ClientError:
            return False


# Global instance
storage_service = StorageService()
