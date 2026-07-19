from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        message = detail["detail"]
    else:
        message = detail

    response.data = {
        "success": False,
        "error": {
            "status_code": response.status_code,
            "message": message,
        },
    }
    return response


def success_response(data: Any = None, status_code: int = status.HTTP_200_OK) -> Response:
    return Response({"success": True, "data": data}, status=status_code)
