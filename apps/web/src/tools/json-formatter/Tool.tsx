"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

export function Tool() {
  const [input, setInput] = useState('{\n  "hello": "world"\n}');
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [indent, setIndent] = useState<2 | 4>(2);
  const { record } = useToolHistory(manifest.id);

  function format(minify = false) {
    setError(null);
    try {
      const parsed: unknown = JSON.parse(input);
      const next = minify ? JSON.stringify(parsed) : JSON.stringify(parsed, null, indent);
      setOutput(next);
      void record(minify ? "minify" : "format", { bytes: next.length });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid JSON");
      setOutput("");
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ToolPanel
        title="Input"
        actions={
          <ToolActions
            onClear={() => {
              setInput("");
              setOutput("");
              setError(null);
            }}
          >
            <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
              <Label htmlFor="indent" className="mb-0">
                Indent
              </Label>
              <select
                id="indent"
                className="rounded border border-[var(--border)] bg-[var(--card)] px-2 py-1"
                value={indent}
                onChange={(e) => setIndent(Number(e.target.value) as 2 | 4)}
              >
                <option value={2}>2</option>
                <option value={4}>4</option>
              </select>
            </div>
            <Button type="button" size="sm" onClick={() => format(false)}>
              Format
            </Button>
            <Button type="button" size="sm" variant="secondary" onClick={() => format(true)}>
              Minify
            </Button>
          </ToolActions>
        }
      >
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="JSON input"
          className="min-h-[280px]"
        />
      </ToolPanel>
      <ToolPanel title="Output" actions={<ToolActions output={output} />}>
        <ToolError message={error} />
        <Textarea
          value={output}
          readOnly
          aria-label="JSON output"
          className="mt-2 min-h-[280px]"
        />
      </ToolPanel>
    </div>
  );
}
