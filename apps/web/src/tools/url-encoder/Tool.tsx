"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

export function Tool() {
  const [input, setInput] = useState("https://toolverse.ai/tools?q=hello world");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { record } = useToolHistory(manifest.id);

  function run(mode: "encode" | "decode") {
    setError(null);
    try {
      const next = mode === "encode" ? encodeURIComponent(input) : decodeURIComponent(input);
      setOutput(next);
      void record(mode);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid URL encoding");
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
            <Button type="button" size="sm" onClick={() => run("encode")}>
              Encode
            </Button>
            <Button type="button" size="sm" variant="secondary" onClick={() => run("decode")}>
              Decode
            </Button>
          </ToolActions>
        }
      >
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="URL input"
          className="min-h-[240px]"
        />
      </ToolPanel>
      <ToolPanel title="Output" actions={<ToolActions output={output} />}>
        <ToolError message={error} />
        <Textarea value={output} readOnly aria-label="URL output" className="mt-2 min-h-[240px]" />
      </ToolPanel>
    </div>
  );
}
