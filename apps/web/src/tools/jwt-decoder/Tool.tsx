"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

function b64urlDecode(segment: string): string {
  const padded = segment.replace(/-/g, "+").replace(/_/g, "/");
  const pad = padded.length % 4 === 0 ? "" : "=".repeat(4 - (padded.length % 4));
  const binary = atob(padded + pad);
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

export function Tool() {
  const sample =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRvb2xWZXJzZSIsImlhdCI6MTUxNjIzOTAyMn0.signature";
  const [input, setInput] = useState(sample);
  const [header, setHeader] = useState("");
  const [payload, setPayload] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { record } = useToolHistory(manifest.id);

  function decode() {
    setError(null);
    try {
      const parts = input.trim().split(".");
      if (parts.length < 2) throw new Error("JWT must have at least header and payload");
      const h = JSON.stringify(JSON.parse(b64urlDecode(parts[0] ?? "")), null, 2);
      const p = JSON.stringify(JSON.parse(b64urlDecode(parts[1] ?? "")), null, 2);
      setHeader(h);
      setPayload(p);
      void record("decode");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid JWT");
      setHeader("");
      setPayload("");
    }
  }

  const combined = [header && `// header\n${header}`, payload && `// payload\n${payload}`]
    .filter(Boolean)
    .join("\n\n");

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ToolPanel
        title="JWT"
        actions={
          <ToolActions
            onClear={() => {
              setInput("");
              setHeader("");
              setPayload("");
              setError(null);
            }}
          >
            <Button type="button" size="sm" onClick={decode}>
              Decode
            </Button>
          </ToolActions>
        }
      >
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="JWT token"
          className="min-h-[260px]"
        />
        <p className="mt-2 text-xs text-[var(--muted)]">
          Signature verification is not performed. Treat tokens as sensitive.
        </p>
      </ToolPanel>
      <div className="space-y-4">
        <ToolError message={error} />
        <ToolPanel title="Header" actions={<ToolActions output={header} />}>
          <Textarea value={header} readOnly aria-label="JWT header" className="min-h-[120px]" />
        </ToolPanel>
        <ToolPanel title="Payload" actions={<ToolActions output={payload || combined} />}>
          <Textarea value={payload} readOnly aria-label="JWT payload" className="min-h-[160px]" />
        </ToolPanel>
      </div>
    </div>
  );
}
