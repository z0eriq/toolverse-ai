"""Cloudflare R2 storage helpers."""

from __future__ import annotations

import logging
from functools import lru_cache

import boto3
from django.conf import settings

logger = logging.getLogger("toolverse.r2")


@lru_cache(maxsize=1)
def get_r2_client():
    if not settings.R2_ENDPOINT_URL or not settings.R2_ACCESS_KEY_ID:
        return None
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str | None:
    client = get_r2_client()
    if client is None:
        logger.warning("R2 is not configured; skip upload for %s", key)
        return None
    client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    if settings.R2_PUBLIC_URL:
        return f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"
    return key
