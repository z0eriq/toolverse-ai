from rest_framework import permissions, serializers, status
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.jobs.models import AsyncJob
from apps.jobs.tasks import execute_tool_job


class JobsThrottle(UserRateThrottle):
    scope = "jobs"


class AsyncJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsyncJob
        fields = (
            "id",
            "tool_id",
            "status",
            "input_payload",
            "output_payload",
            "error",
            "progress",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class JobCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = (JobsThrottle,)

    def post(self, request):
        tool_id = request.data.get("tool_id")
        if not tool_id:
            from rest_framework.response import Response

            return Response(
                {"success": False, "error": {"message": "tool_id required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job = AsyncJob.objects.create(
            user=request.user,
            tool_id=tool_id,
            input_payload=request.data.get("input") or request.data.get("payload") or {},
        )
        async_result = execute_tool_job.delay(str(job.id))
        job.celery_task_id = async_result.id or ""
        job.save(update_fields=["celery_task_id", "updated_at"])
        return success_response(AsyncJobSerializer(job).data, status_code=status.HTTP_202_ACCEPTED)


class JobDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, job_id):
        try:
            job = AsyncJob.objects.get(pk=job_id, user=request.user)
        except AsyncJob.DoesNotExist:
            from rest_framework.response import Response

            return Response(
                {"success": False, "error": {"message": "Job not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return success_response(AsyncJobSerializer(job).data)
