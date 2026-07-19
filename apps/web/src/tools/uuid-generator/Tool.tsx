"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

export function Tool() {
  const [count, setCount] = useState(5);
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { record } = useToolHistory(manifest.id);

  function generate() {
    setError(null);
    const n = Math.min(200, Math.max(1, Math.floor(count) || 1));
    try {
      const lines = Array.from({ length: n }, () => crypto.randomUUID());
      setOutput(lines.join("\n"));
      void record("generate", { count: n });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to generate UUIDs");
    }
  }

  return (
    <ToolPanel
      title="UUID v4"
      actions={
        <ToolActions
          output={output}
          onClear={() => {
            setOutput("");
            setError(null);
          }}
        >
          <Button type="button" size="sm" onClick={generate}>
            Generate
          </Button>
        </ToolActions>
      }
    >
      <div className="mb-4 max-w-xs">
        <Label htmlFor="count">Count (1–200)</Label>
        <Input
          id="count"
          type="number"
          min={1}
          max={200}
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
        />
      </div>
      <ToolError message={error} />
      <Textarea
        value={output}
        readOnly
        aria-label="Generated UUIDs"
        className="mt-2 min-h-[240px]"
        placeholder="Click Generate to create UUIDs"
      />
    </ToolPanel>
  );
}
