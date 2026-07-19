from __future__ import annotations

from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.keywords.models import KeywordOpportunity
from apps.keywords.serializers import KeywordOpportunitySerializer


class KeywordOpportunityListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = KeywordOpportunity.objects.all().order_by("-priority_score", "-impressions")
        locale = request.query_params.get("locale")
        if locale:
            qs = qs.filter(locale=locale)
        limit = min(int(request.query_params.get("limit") or 100), 500)
        qs = qs[:limit]
        return success_response(KeywordOpportunitySerializer(qs, many=True).data)


class KeywordOpportunityTopView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        limit = min(int(request.query_params.get("limit") or 50), 200)
        qs = KeywordOpportunity.objects.all().order_by("-priority_score")[:limit]
        return success_response(KeywordOpportunitySerializer(qs, many=True).data)
