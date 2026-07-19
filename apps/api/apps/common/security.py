"""Upload and request security helpers."""

from __future__ import annotations

from typing import Iterable

from rest_framework.exceptions import ValidationError


def validate_upload(
    file,
    allowed_types: Iterable[str],
    max_bytes: int,
) -> None:
    """
    Validate an uploaded file's size and content type.

    Raises ``ValidationError`` when the file is missing, too large, or has
    a disallowed content type. Content-type checks use the uploaded file's
    ``content_type`` attribute (browser-provided); callers that need magic-byte
    sniffing should layer that on top.
    """
    if file is None:
        raise ValidationError({"file": "No file provided"})

    size = getattr(file, "size", None)
    if size is None:
        raise ValidationError({"file": "Unable to determine file size"})
    if size > max_bytes:
        raise ValidationError(
            {"file": f"File exceeds maximum size of {max_bytes} bytes"}
        )
    if size < 1:
        raise ValidationError({"file": "File is empty"})

    allowed = {t.lower().strip() for t in allowed_types if t}
    content_type = (getattr(file, "content_type", None) or "").lower().strip()
    if allowed and content_type not in allowed:
        raise ValidationError(
            {
                "file": (
                    f"Content type '{content_type or 'unknown'}' is not allowed. "
                    f"Allowed: {', '.join(sorted(allowed))}"
                )
            }
        )
