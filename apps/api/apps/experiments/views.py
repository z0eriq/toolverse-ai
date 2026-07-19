from __future__ import annotations

import uuid

from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.experiments.models import Experiment
from apps.experiments.serializers import (
    AssignQuerySerializer,
    ExperimentSerializer,
    TrackEventSerializer,
)
from apps.experiments.services import assign_experiment, experiment_results, track_event


class ExperimentAssignView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        ser = AssignQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        key = ser.validated_data["key"]
        subject_key = (ser.validated_data.get("subject_key") or "").strip()
        if not subject_key:
            subject_key = request.headers.get("X-Experiment-Subject") or str(uuid.uuid4())
        try:
            assignment = assign_experiment(
                key,
                subject_key,
                user=request.user if request.user.is_authenticated else None,
            )
        except Experiment.DoesNotExist as exc:
            raise NotFound("Experiment not found or inactive") from exc
        return success_response(
            {
                "key": key,
                "subject_key": assignment.subject_key,
                "variant": assignment.variant,
                "assignment_id": assignment.pk,
            }
        )


class ExperimentTrackView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        ser = TrackEventSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            event = track_event(
                key=ser.validated_data["key"],
                subject_key=ser.validated_data["subject_key"],
                event_name=ser.validated_data["event_name"],
                properties=ser.validated_data.get("properties") or {},
            )
        except Experiment.DoesNotExist as exc:
            raise NotFound("Experiment not found") from exc
        return success_response(
            {
                "id": event.pk,
                "key": ser.validated_data["key"],
                "event_name": event.event_name,
                "variant": event.variant,
            },
            status_code=status.HTTP_201_CREATED,
        )


class AdminExperimentListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = Experiment.objects.all().order_by("key")
        return success_response(ExperimentSerializer(qs, many=True).data)


class AdminExperimentResultsView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request, pk: int):
        try:
            experiment = Experiment.objects.get(pk=pk)
        except Experiment.DoesNotExist as exc:
            raise NotFound("Experiment not found") from exc
        return success_response(experiment_results(experiment))
