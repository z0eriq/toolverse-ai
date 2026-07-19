from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.launch_readiness.services import readiness_payload, run_readiness_checks


class LaunchReadinessView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        return success_response(readiness_payload())

    def post(self, request):
        checks = run_readiness_checks()
        return success_response(
            [
                {
                    "id": c.id,
                    "key": c.key,
                    "category": c.category,
                    "status": c.status,
                    "detail": c.detail,
                    "checked_at": c.checked_at.isoformat() if c.checked_at else None,
                }
                for c in checks
            ],
            status_code=status.HTTP_200_OK,
        )
