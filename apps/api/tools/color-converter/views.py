"""HEX / RGB / HSL color conversion and WCAG contrast API."""

from __future__ import annotations

import colorsys
import re
from typing import Any

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class ToolThrottle(AnonRateThrottle):
    scope = "tool"


def _error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response(
        {"success": False, "error": {"status_code": status_code, "message": message}},
        status=status_code,
    )


def _parse_hex(value: str) -> tuple[int, int, int, float]:
    match = _HEX_RE.match(value.strip())
    if not match:
        raise ValueError("Invalid HEX color. Use #RGB, #RRGGBB, or #RRGGBBAA.")
    h = match.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
        alpha = 1.0
    elif len(h) == 6:
        alpha = 1.0
    else:
        alpha = int(h[6:8], 16) / 255.0
        h = h[:6]
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r, g, b, alpha


def _parse_rgb(value: Any) -> tuple[int, int, int, float]:
    if isinstance(value, dict):
        r, g, b = value.get("r"), value.get("g"), value.get("b")
        a = value.get("a", 1)
    elif isinstance(value, (list, tuple)) and len(value) >= 3:
        r, g, b = value[0], value[1], value[2]
        a = value[3] if len(value) > 3 else 1
    elif isinstance(value, str):
        nums = re.findall(r"[\d.]+", value)
        if len(nums) < 3:
            raise ValueError("Invalid RGB value.")
        r, g, b = nums[0], nums[1], nums[2]
        a = nums[3] if len(nums) > 3 else 1
    else:
        raise ValueError("RGB must be an object, array, or css-like string.")

    try:
        ri, gi, bi = int(round(float(r))), int(round(float(g))), int(round(float(b)))
        af = float(a)
    except (TypeError, ValueError) as exc:
        raise ValueError("RGB channels must be numbers.") from exc

    for channel, name in ((ri, "r"), (gi, "g"), (bi, "b")):
        if channel < 0 or channel > 255:
            raise ValueError(f"RGB channel '{name}' must be between 0 and 255.")
    if af < 0 or af > 1:
        raise ValueError("Alpha must be between 0 and 1.")
    return ri, gi, bi, af


def _parse_hsl(value: Any) -> tuple[int, int, int, float]:
    if isinstance(value, dict):
        h, s, light = value.get("h"), value.get("s"), value.get("l")
        a = value.get("a", 1)
    elif isinstance(value, (list, tuple)) and len(value) >= 3:
        h, s, light = value[0], value[1], value[2]
        a = value[3] if len(value) > 3 else 1
    elif isinstance(value, str):
        nums = re.findall(r"[\d.]+", value)
        if len(nums) < 3:
            raise ValueError("Invalid HSL value.")
        h, s, light = nums[0], nums[1], nums[2]
        a = nums[3] if len(nums) > 3 else 1
    else:
        raise ValueError("HSL must be an object, array, or css-like string.")

    try:
        hf, sf, lf, af = float(h), float(s), float(light), float(a)
    except (TypeError, ValueError) as exc:
        raise ValueError("HSL channels must be numbers.") from exc

    if sf > 1:
        sf /= 100.0
    if lf > 1:
        lf /= 100.0
    if hf < 0 or hf > 360:
        raise ValueError("Hue must be between 0 and 360.")
    if sf < 0 or sf > 1 or lf < 0 or lf > 1:
        raise ValueError("Saturation and lightness must be between 0 and 100% (or 0–1).")
    if af < 0 or af > 1:
        raise ValueError("Alpha must be between 0 and 1.")

    r_f, g_f, b_f = colorsys.hls_to_rgb(hf / 360.0, lf, sf)
    return (
        int(round(r_f * 255)),
        int(round(g_f * 255)),
        int(round(b_f * 255)),
        af,
    )


def _parse_any(value: Any) -> tuple[int, int, int, float]:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered.startswith("rgb"):
            return _parse_rgb(value)
        if lowered.startswith("hsl"):
            return _parse_hsl(value)
        return _parse_hex(value)
    if isinstance(value, dict):
        if "r" in value:
            return _parse_rgb(value)
        if "h" in value and ("s" in value or "l" in value):
            return _parse_hsl(value)
        if "hex" in value:
            return _parse_hex(str(value["hex"]))
    if isinstance(value, (list, tuple)):
        return _parse_rgb(value)
    raise ValueError("Unrecognized color value.")


def _resolve_primary(payload: dict[str, Any]) -> tuple[int, int, int, float]:
    if payload.get("hex") is not None:
        return _parse_hex(str(payload["hex"]))
    if payload.get("rgb") is not None:
        return _parse_rgb(payload["rgb"])
    if payload.get("hsl") is not None:
        return _parse_hsl(payload["hsl"])
    if payload.get("color") is not None:
        return _parse_any(payload["color"])
    if payload.get("foreground") is not None:
        return _parse_any(payload["foreground"])
    raise ValueError("Provide a color via 'hex', 'rgb', 'hsl', 'color', or 'foreground'.")


def _to_formats(r: int, g: int, b: int, a: float) -> dict[str, Any]:
    hex6 = f"#{r:02X}{g:02X}{b:02X}"
    hex8 = f"#{r:02X}{g:02X}{b:02X}{int(round(a * 255)):02X}" if a < 1 else hex6
    h_f, l_f, s_f = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    h = round(h_f * 360, 2)
    s = round(s_f * 100, 2)
    light = round(l_f * 100, 2)
    return {
        "hex": hex6,
        "hexAlpha": hex8,
        "rgb": {"r": r, "g": g, "b": b, "a": round(a, 4)},
        "rgbString": f"rgb({r}, {g}, {b})" if a >= 1 else f"rgba({r}, {g}, {b}, {round(a, 4)})",
        "hsl": {"h": h, "s": s, "l": light, "a": round(a, 4)},
        "hslString": (
            f"hsl({h}, {s}%, {light}%)"
            if a >= 1
            else f"hsla({h}, {s}%, {light}%, {round(a, 4)})"
        ),
    }


def _relative_luminance(r: int, g: int, b: int) -> float:
    def channel(c: int) -> float:
        srgb = c / 255.0
        return srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    l1 = _relative_luminance(*c1)
    l2 = _relative_luminance(*c2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ToolThrottle])
def color_converter_view(request) -> Response:
    """
    Body examples:
      { "hex": "#0ea5e9" }
      { "rgb": { "r": 14, "g": 165, "b": 233 } }
      { "hsl": { "h": 199, "s": 89, "l": 48 } }
      { "hex": "#0ea5e9", "background": "#ffffff" }
      { "foreground": "#111111", "background": "#ffffff" }
    """
    payload = request.data if isinstance(request.data, dict) else {}

    try:
        r, g, b, a = _resolve_primary(payload)
        primary = _to_formats(r, g, b, a)

        background = None
        contrast = None
        if payload.get("background") is not None:
            br, bg, bb, ba = _parse_any(payload["background"])
            background = _to_formats(br, bg, bb, ba)
            ratio = _contrast_ratio((r, g, b), (br, bg, bb))
            contrast = {
                "ratio": ratio,
                "aa": {"normal": ratio >= 4.5, "large": ratio >= 3.0},
                "aaa": {"normal": ratio >= 7.0, "large": ratio >= 4.5},
            }
    except ValueError as exc:
        return _error(str(exc))

    return Response(
        {
            "success": True,
            "data": {
                "color": primary,
                "background": background,
                "contrast": contrast,
            },
        }
    )
