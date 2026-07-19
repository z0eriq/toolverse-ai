from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.workflows.models import Workflow, WorkflowTemplate, WorkflowUsageDaily
from apps.workflows.serializers import (
    WorkflowRunSerializer,
    WorkflowSerializer,
    WorkflowTemplateSerializer,
    WorkflowUsageDailySerializer,
)
from apps.workflows.services import run_workflow


class WorkflowListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkflowSerializer

    def get_queryset(self):
        return Workflow.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(owner=request.user)
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class WorkflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkflowSerializer

    def get_queryset(self):
        return Workflow.objects.filter(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response({"deleted": True})


class WorkflowRunView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk: int):
        try:
            workflow = Workflow.objects.get(pk=pk, owner=request.user)
        except Workflow.DoesNotExist as exc:
            raise NotFound("Workflow not found") from exc
        input_data = request.data.get("input")
        if input_data is None:
            input_data = {k: v for k, v in request.data.items() if k != "input"}
        if not isinstance(input_data, dict):
            raise ValidationError({"input": "Must be an object"})
        run = run_workflow(workflow, input_data, user=request.user)
        return success_response(
            WorkflowRunSerializer(run).data,
            status_code=status.HTTP_201_CREATED,
        )


class WorkflowSharedView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token: str):
        try:
            workflow = Workflow.objects.get(share_token=token)
        except (Workflow.DoesNotExist, ValueError) as exc:
            raise NotFound("Shared workflow not found") from exc
        if workflow.visibility == Workflow.Visibility.PRIVATE:
            raise NotFound("Shared workflow not found")
        return success_response(WorkflowSerializer(workflow).data)


class WorkflowTemplateListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        qs = WorkflowTemplate.objects.filter(is_public=True).order_by("name")
        return success_response(WorkflowTemplateSerializer(qs, many=True).data)


class WorkflowUsageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        qs = WorkflowUsageDaily.objects.filter(workflow__owner=request.user).select_related(
            "workflow"
        ).order_by("-date")[:90]
        return success_response(WorkflowUsageDailySerializer(qs, many=True).data)


class AdminWorkflowTemplateListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = WorkflowTemplate.objects.all().order_by("name")
        return success_response(WorkflowTemplateSerializer(qs, many=True).data)
