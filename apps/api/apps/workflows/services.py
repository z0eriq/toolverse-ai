from __future__ import annotations

import base64
import json
import logging
import time
from typing import Any

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.workflows.models import Workflow, WorkflowRun, WorkflowUsageDaily

logger = logging.getLogger("toolverse.workflows")


def _apply_input_map(payload: dict[str, Any], input_map: dict[str, Any] | None) -> dict[str, Any]:
    if not input_map:
        return payload
    mapped: dict[str, Any] = {}
    for key, source in input_map.items():
        if isinstance(source, str) and source.startswith("input."):
            mapped[key] = payload.get(source.split(".", 1)[1])
        elif isinstance(source, str) and source.startswith("{{") and source.endswith("}}"):
            inner = source[2:-2].strip()
            if inner.startswith("input."):
                mapped[key] = payload.get(inner.split(".", 1)[1])
            else:
                mapped[key] = payload.get(inner, source)
        else:
            mapped[key] = source
    return {**payload, **mapped}


def _run_transform(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Pass-through transform ops (includes base64 / json helpers)."""
    op = step.get("op") or step.get("tool_slug") or "identity"
    source = step.get("source", "input")
    target = step.get("target", "output")

    value: Any
    if source == "input":
        value = context.get("input")
    elif source == "output":
        value = context.get("output")
    elif source.startswith("vars."):
        value = (context.get("vars") or {}).get(source.split(".", 1)[1])
    elif source.startswith("input."):
        value = (context.get("input") or {}).get(source.split(".", 1)[1])
    else:
        value = context.get(source, context.get("output", context.get("input")))

    # Prefer text field when operating on dict inputs
    if isinstance(value, dict) and "text" in value and op in {
        "uppercase",
        "lowercase",
        "trim",
        "base64_encode",
        "base64_decode",
        "word_count",
    }:
        value = value.get("text")

    if op == "uppercase" and isinstance(value, str):
        result = value.upper()
    elif op == "lowercase" and isinstance(value, str):
        result = value.lower()
    elif op == "trim" and isinstance(value, str):
        result = value.strip()
    elif op == "json_stringify":
        result = json.dumps(value, ensure_ascii=False, indent=2)
    elif op == "json_parse" and isinstance(value, str):
        result = json.loads(value)
    elif op == "json_format" and isinstance(value, str):
        result = json.dumps(json.loads(value), ensure_ascii=False, indent=2)
    elif op == "base64_encode":
        raw = value if isinstance(value, str) else json.dumps(value)
        result = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    elif op == "base64_decode" and isinstance(value, str):
        result = base64.b64decode(value.encode("ascii")).decode("utf-8")
    elif op == "word_count" and isinstance(value, str):
        result = {"words": len(value.split()), "chars": len(value)}
    else:
        # identity / unknown op pass-through
        result = value

    if target.startswith("vars."):
        context.setdefault("vars", {})[target.split(".", 1)[1]] = result
    else:
        context["output"] = result
    return context


def _run_tool_step(step: dict[str, Any], context: dict[str, Any], *, user=None) -> dict[str, Any]:
    slug = step.get("tool_slug") or step.get("slug") or ""
    payload = _apply_input_map(
        {"input": context.get("input"), "output": context.get("output"), **(context.get("vars") or {})},
        step.get("input_map"),
    )
    tool_input = payload.get("input") if isinstance(payload.get("input"), dict) else payload
    if context.get("output") is not None and "text" not in (tool_input or {}):
        # Feed previous output forward
        if isinstance(tool_input, dict):
            tool_input = {**tool_input, "text": context.get("output")}
        else:
            tool_input = {"text": context.get("output")}

    try:
        from apps.tools_registry.dynamic_runtime import execute_dynamic_pipeline

        result = execute_dynamic_pipeline(slug, {"input": tool_input}, user=user)
        context["output"] = result.get("output")
        context.setdefault("vars", {})[f"step_{slug}"] = result
        return context
    except Exception as exc:  # noqa: BLE001
        logger.info("tool step %s fell back to transform: %s", slug, exc)
        # Fall back: treat missing tools as transform using tool_slug as op hint
        fallback = {**step, "type": "transform", "op": step.get("op") or "identity"}
        return _run_transform(fallback, context)


@transaction.atomic
def run_workflow(workflow: Workflow, input_data: dict[str, Any] | None, user=None) -> WorkflowRun:
    """Execute workflow steps sequentially and record WorkflowRun + daily usage."""
    started = time.perf_counter()
    run = WorkflowRun.objects.create(
        workflow=workflow,
        user=user,
        status=WorkflowRun.Status.RUNNING,
        input=input_data or {},
    )
    context: dict[str, Any] = {
        "input": input_data or {},
        "vars": {},
        "output": None,
    }
    steps = workflow.steps if isinstance(workflow.steps, list) else []

    try:
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_type = (step.get("type") or "").lower()
            if step_type in {"tool", "tool_slug"} or step.get("tool_slug"):
                if step_type == "transform":
                    context = _run_transform(step, context)
                else:
                    context = _run_tool_step(step, context, user=user)
            elif step_type in {"transform", "op", ""} or step.get("op"):
                context = _run_transform(step, context)
            else:
                context = _run_transform(step, context)

        run.status = WorkflowRun.Status.SUCCESS
        run.output = {
            "output": context.get("output"),
            "vars": context.get("vars") or {},
        }
        run.error = ""
    except Exception as exc:  # noqa: BLE001
        logger.exception("workflow run failed")
        run.status = WorkflowRun.Status.FAILED
        run.error = str(exc)[:2000]
        run.output = {"output": context.get("output"), "vars": context.get("vars") or {}}

    run.duration_ms = int((time.perf_counter() - started) * 1000)
    run.save(update_fields=["status", "output", "error", "duration_ms", "updated_at"])

    today = timezone.now().date()
    usage, created = WorkflowUsageDaily.objects.get_or_create(
        workflow=workflow,
        date=today,
        defaults={"runs": 1},
    )
    if not created:
        WorkflowUsageDaily.objects.filter(pk=usage.pk).update(runs=F("runs") + 1)

    return run
