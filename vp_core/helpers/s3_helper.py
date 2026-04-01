import asyncio
from typing import Any

import boto3

from vp_core.logging.logger import setup_logger

logger = setup_logger()


class S3Helper:
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
    ):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    async def get_object(self, bucket_name: str, key: str) -> Any:
        """
        Retrieves an object from S3 asynchronously using a thread.
        """
        return await asyncio.to_thread(self.s3_client.get_object, Bucket=bucket_name, Key=key)

    async def put_object(
        self,
        bucket_name: str,
        body: Any,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        """
        Uploads a body to a specific S3 key asynchronously using a thread.
        Returns the object_key on success, and raises an Exception on failure.
        """
        extra_args = {"ACL": "public-read"}
        if content_type:
            extra_args["ContentType"] = content_type

        await asyncio.to_thread(
            self.s3_client.put_object,
            Bucket=bucket_name,
            Key=object_key,
            Body=body,
            **extra_args,
        )
        return object_key

