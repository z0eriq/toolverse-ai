from __future__ import annotations

import hashlib
from typing import Any

from django.db.models import Count

from apps.experiments.models import Experiment, ExperimentAssignment, ExperimentEvent


def _pick_variant(experiment: Experiment, subject_key: str) -> str:
    variants = experiment.variants or []
    if not variants:
        return "control"
    # Deterministic weighted assignment
    total = sum(max(int(v.get("weight") or 0), 0) for v in variants) or len(variants)
    digest = hashlib.sha256(f"{experiment.key}:{subject_key}".encode()).hexdigest()
    bucket = int(digest[:8], 16) % total
    cursor = 0
    for v in variants:
        weight = max(int(v.get("weight") or 0), 0) or 1
        cursor += weight
        if bucket < cursor:
            return str(v.get("key") or "control")
    return str(variants[-1].get("key") or "control")


def assign_experiment(
    key: str,
    subject_key: str,
    *,
    user=None,
) -> ExperimentAssignment:
    experiment = Experiment.objects.get(key=key, is_active=True)
    existing = ExperimentAssignment.objects.filter(
        experiment=experiment,
        subject_key=subject_key,
    ).first()
    if existing:
        return existing
    variant = _pick_variant(experiment, subject_key)
    return ExperimentAssignment.objects.create(
        experiment=experiment,
        subject_key=subject_key,
        variant=variant,
        user=user if getattr(user, "is_authenticated", False) else None,
    )


def track_event(
    *,
    key: str,
    subject_key: str,
    event_name: str,
    properties: dict[str, Any] | None = None,
) -> ExperimentEvent:
    experiment = Experiment.objects.get(key=key)
    assignment = ExperimentAssignment.objects.filter(
        experiment=experiment,
        subject_key=subject_key,
    ).first()
    return ExperimentEvent.objects.create(
        experiment=experiment,
        assignment=assignment,
        subject_key=subject_key,
        variant=assignment.variant if assignment else "",
        event_name=event_name[:128],
        properties=properties or {},
    )


def experiment_results(experiment: Experiment) -> dict[str, Any]:
    assignments = (
        ExperimentAssignment.objects.filter(experiment=experiment)
        .values("variant")
        .annotate(count=Count("id"))
        .order_by("variant")
    )
    events = (
        ExperimentEvent.objects.filter(experiment=experiment)
        .values("variant", "event_name")
        .annotate(count=Count("id"))
        .order_by("variant", "event_name")
    )
    return {
        "key": experiment.key,
        "name": experiment.name,
        "is_active": experiment.is_active,
        "assignments": list(assignments),
        "events": list(events),
        "total_assignments": ExperimentAssignment.objects.filter(experiment=experiment).count(),
        "total_events": ExperimentEvent.objects.filter(experiment=experiment).count(),
    }
