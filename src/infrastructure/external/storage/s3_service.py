"""AWS S3 storage service implementation."""

import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from src.core.config.settings import settings
from src.core.exceptions import StorageError
from src.domain.interfaces.services import IStorageService


class S3StorageService(IStorageService):
    """Storage service implementation using AWS S3."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket_name = settings.s3_bucket_name

    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        folder: str = "lessons",
    ) -> str:
        """Upload a file to S3."""
        try:
            # Generate unique key
            file_extension = file_name.split(".")[-1] if "." in file_name else ""
            unique_key = f"{folder}/{uuid.uuid4()}.{file_extension}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_key,
                Body=file_content,
                ContentType=content_type,
            )

            # Return the S3 URL
            return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{unique_key}"

        except ClientError as e:
            raise StorageError(
                message=f"Failed to upload file: {str(e)}",
                bucket=self.bucket_name,
            )

    async def download_file(self, file_url: str) -> bytes:
        """Download a file from S3."""
        try:
            key = self._extract_key_from_url(file_url)

            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            return response["Body"].read()

        except ClientError as e:
            raise StorageError(
                message=f"Failed to download file: {str(e)}",
                bucket=self.bucket_name,
            )

    async def delete_file(self, file_url: str) -> bool:
        """Delete a file from S3."""
        try:
            key = self._extract_key_from_url(file_url)

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            return True

        except ClientError as e:
            raise StorageError(
                message=f"Failed to delete file: {str(e)}",
                bucket=self.bucket_name,
            )

    async def get_signed_url(
        self,
        file_url: str,
        expires_in: int = 3600,
    ) -> str:
        """Get a presigned URL for temporary access."""
        try:
            key = self._extract_key_from_url(file_url)

            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                },
                ExpiresIn=expires_in,
            )

            return url

        except ClientError as e:
            raise StorageError(
                message=f"Failed to generate signed URL: {str(e)}",
                bucket=self.bucket_name,
            )

    def _extract_key_from_url(self, url: str) -> str:
        """Extract S3 key from URL."""
        # Handle different URL formats
        if f"{self.bucket_name}.s3" in url:
            # Format: https://bucket.s3.region.amazonaws.com/key
            parts = url.split(f".amazonaws.com/")
            if len(parts) == 2:
                return parts[1]

        if f"s3.amazonaws.com/{self.bucket_name}" in url:
            # Format: https://s3.amazonaws.com/bucket/key
            parts = url.split(f"/{self.bucket_name}/")
            if len(parts) == 2:
                return parts[1]

        # Assume it's just the key
        return url
