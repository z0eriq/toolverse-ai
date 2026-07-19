"use client";

import { useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n));
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const cleaned = hex.replace("#", "").trim();
  const full =
    cleaned.length === 3
      ? cleaned
          .split("")
          .map((c) => c + c)
          .join("")
      : cleaned;
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return null;
  return {
    r: parseInt(full.slice(0, 2), 16),
    g: parseInt(full.slice(2, 4), 16),
    b: parseInt(full.slice(4, 6), 16),
  };
}

function rgbToHex(r: number, g: number, b: number): string {
  return `#${[r, g, b]
    .map((v) => clamp(Math.round(v), 0, 255).toString(16).padStart(2, "0"))
    .join("")}`;
}

function rgbToHsl(r: number, g: number, b: number) {
  const rn = r / 255;
  const gn = g / 255;
  const bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const l = (max + min) / 2;
  if (max === min) return { h: 0, s: 0, l: Math.round(l * 100) };
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h = 0;
  switch (max) {
    case rn:
      h = (gn - bn) / d + (gn < bn ? 6 : 0);
      break;
    case gn:
      h = (bn - rn) / d + 2;
      break;
    default:
      h = (rn - gn) / d + 4;
  }
  h /= 6;
  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100),
  };
}

export function Tool() {
  const [hex, setHex] = useState("#14b8a6");
  const [error, setError] = useState<string | null>(null);
  const { record } = useToolHistory(manifest.id);

  const converted = useMemo(() => {
    const rgb = hexToRgb(hex);
    if (!rgb) return null;
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    return {
      hex: rgbToHex(rgb.r, rgb.g, rgb.b),
      rgb: `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`,
      hsl: `hsl(${hsl.h}, ${hsl.s}%, ${hsl.l}%)`,
      raw: rgb,
    };
  }, [hex]);

  function onHexChange(value: string) {
    setHex(value);
    const rgb = hexToRgb(value);
    if (!rgb) {
      setError("Enter a valid HEX color (#RGB or #RRGGBB)");
      return;
    }
    setError(null);
    void record("convert", { hex: rgbToHex(rgb.r, rgb.g, rgb.b) });
  }

  const copyAll = converted
    ? `${converted.hex}\n${converted.rgb}\n${converted.hsl}`
    : "";

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
      <ToolPanel title="Convert" actions={<ToolActions output={copyAll} />}>
        <div className="max-w-sm space-y-3">
          <div>
            <Label htmlFor="hex">HEX</Label>
            <Input
              id="hex"
              value={hex}
              onChange={(e) => onHexChange(e.target.value)}
              aria-invalid={Boolean(error)}
            />
          </div>
          <div>
            <Label htmlFor="picker">Picker</Label>
            <Input
              id="picker"
              type="color"
              value={converted?.hex ?? "#14b8a6"}
              onChange={(e) => onHexChange(e.target.value)}
              className="h-12 cursor-pointer p-1"
            />
          </div>
        </div>
        <ToolError message={error} />
        {converted ? (
          <dl className="mt-4 grid gap-3 sm:grid-cols-3">
            {[
              ["HEX", converted.hex],
              ["RGB", converted.rgb],
              ["HSL", converted.hsl],
            ].map(([label, value]) => (
              <div key={label} className="rounded-[var(--radius-md)] border border-[var(--border)] p-3">
                <dt className="text-xs uppercase tracking-wider text-[var(--muted)]">{label}</dt>
                <dd className="mt-1 font-mono text-sm">{value}</dd>
              </div>
            ))}
          </dl>
        ) : null}
      </ToolPanel>
      <div
        className="surface min-h-[220px] rounded-[var(--radius-lg)] border-2"
        style={{ backgroundColor: converted?.hex ?? "transparent" }}
        role="img"
        aria-label={converted ? `Color preview ${converted.hex}` : "Invalid color"}
      />
    </div>
  );
}
