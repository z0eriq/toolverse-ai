"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

type Algo = "SHA-1" | "SHA-256" | "SHA-512";

async function digest(algo: Algo, text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const buf = await crypto.subtle.digest(algo, data);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function Tool() {
  const [input, setInput] = useState("ToolVerse AI");
  const [algo, setAlgo] = useState<Algo>("SHA-256");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const { record } = useToolHistory(manifest.id);

  async function run() {
    setBusy(true);
    setError(null);
    try {
      const next = await digest(algo, input);
      setOutput(next);
      void record("hash", { algorithm: algo });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Hash failed");
      setOutput("");
    } finally {
      setBusy(false);
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
            <div className="flex items-center gap-2">
              <Label htmlFor="algo" className="mb-0 text-xs">
                Algorithm
              </Label>
              <select
                id="algo"
                className="rounded border border-[var(--border)] bg-[var(--card)] px-2 py-1 text-sm"
                value={algo}
                onChange={(e) => setAlgo(e.target.value as Algo)}
              >
                <option value="SHA-1">SHA-1</option>
                <option value="SHA-256">SHA-256</option>
                <option value="SHA-512">SHA-512</option>
              </select>
            </div>
            <Button type="button" size="sm" disabled={busy} onClick={() => void run()}>
              Hash
            </Button>
          </ToolActions>
        }
      >
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Hash input"
          className="min-h-[240px]"
        />
      </ToolPanel>
      <ToolPanel title="Digest (hex)" actions={<ToolActions output={output} />}>
        <ToolError message={error} />
        <Textarea value={output} readOnly aria-label="Hash output" className="mt-2 min-h-[240px]" />
      </ToolPanel>
    </div>
  );
}
