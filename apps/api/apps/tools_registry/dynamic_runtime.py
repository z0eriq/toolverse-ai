"""Generic pipeline executor for DB-defined dynamic tools."""

from __future__ import annotations

import json
import re
from typing import Any

from django.template import Context, Template


def execute_dynamic_pipeline(slug: str, payload: dict[str, Any], *, user=None) -> dict[str, Any]:
    from apps.tools_registry.dynamic_models import DynamicToolDefinition

    definition = DynamicToolDefinition.objects.get(
        slug=slug,
        status=DynamicToolDefinition.Status.PUBLISHED,
    )
    context: dict[str, Any] = {
        "input": payload.get("input") or payload,
        "vars": {},
        "output": None,
    }
    steps = definition.pipeline if isinstance(definition.pipeline, list) else []
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_type = step.get("type")
        if step_type == "transform":
            context = _step_transform(step, context)
        elif step_type == "template":
            context = _step_template(step, context)
        elif step_type == "ai":
            context = _step_ai(step, context, user=user, tool_id=f"dynamic:{slug}")
        elif step_type == "http":
            context = _step_http(step, context)
        else:
            raise ValueError(f"Unknown pipeline step type: {step_type}")

    return {
        "slug": slug,
        "output": context.get("output"),
        "vars": context.get("vars"),
    }


def _render_string(template_str: str, context: dict[str, Any]) -> str:
    # Simple {{var}} substitution plus Django Template for advanced cases
    data = {
        **(context.get("input") or {}),
        **(context.get("vars") or {}),
        "output": context.get("output"),
    }

    def repl(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        val = data.get(key, "")
        if isinstance(val, (dict, list)):
            return json.dumps(val)
        return str(val)

    rendered = re.sub(r"\{\{\s*([\w.]+)\s*\}\}", repl, template_str)
    try:
        return Template(rendered).render(Context(data))
    except Exception:  # noqa: BLE001
        return rendered


def _step_transform(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    op = step.get("op", "identity")
    source = step.get("source", "input")
    target = step.get("target", "output")
    value = context.get(source)
    if source.startswith("vars."):
        value = (context.get("vars") or {}).get(source.split(".", 1)[1])
    elif source.startswith("input."):
        value = (context.get("input") or {}).get(source.split(".", 1)[1])

    if op == "uppercase" and isinstance(value, str):
        result = value.upper()
    elif op == "lowercase" and isinstance(value, str):
        result = value.lower()
    elif op == "json_stringify":
        result = json.dumps(value, ensure_ascii=False, indent=2)
    elif op == "json_parse" and isinstance(value, str):
        result = json.loads(value)
    elif op == "trim" and isinstance(value, str):
        result = value.strip()
    elif op == "word_count" and isinstance(value, str):
        result = {"words": len(value.split()), "chars": len(value)}
    else:
        result = value

    if target.startswith("vars."):
        context.setdefault("vars", {})[target.split(".", 1)[1]] = result
    else:
        context["output"] = result
    return context


def _step_template(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    template_str = step.get("template") or "{{output}}"
    rendered = _render_string(template_str, context)
    target = step.get("target", "output")
    if target.startswith("vars."):
        context.setdefault("vars", {})[target.split(".", 1)[1]] = rendered
    else:
        context["output"] = rendered
    return context


def _step_ai(step: dict[str, Any], context: dict[str, Any], *, user=None, tool_id: str = "") -> dict[str, Any]:
    from apps.ai_providers.router import get_ai_router

    prompt_template = step.get("prompt") or "{{input.text}}"
    prompt = _render_string(prompt_template, context)
    system = step.get("system") or "You are a helpful assistant for ToolVerse AI tools."
    result = get_ai_router().complete(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        provider=step.get("provider"),
        model=step.get("model"),
        temperature=float(step.get("temperature", 0.2)),
        max_tokens=int(step.get("max_tokens", 1024)),
        user=user,
        tool_id=tool_id,
    )
    context["output"] = result.content
    context.setdefault("vars", {})["ai_provider"] = result.provider
    context.setdefault("vars", {})["ai_model"] = result.model
    return context


def _step_http(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    import json as _json
    import urllib.request

    url = _render_string(step.get("url") or "", context)
    method = (step.get("method") or "GET").upper()
    headers = step.get("headers") or {"Content-Type": "application/json"}
    body = step.get("body")
    data = None
    if body is not None:
        if isinstance(body, str):
            data = _render_string(body, context).encode("utf-8")
        else:
            data = _json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=int(step.get("timeout", 30))) as resp:
        raw = resp.read().decode("utf-8")
    try:
        parsed = _json.loads(raw)
    except _json.JSONDecodeError:
        parsed = raw
    context["output"] = parsed
    return context
