"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

function encodeUtf8(text: string): string {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  bytes.forEach((b) => {
    binary += String.fromCharCode(b);
  });
  return btoa(binary);
}

function decodeUtf8(b64: string): string {
  const binary = atob(b64.replace(/\s/g, ""));
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

export function Tool() {
  const [input, setInput] = useState("Hello ToolVerse");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { record } = useToolHistory(manifest.id);

  function run(mode: "encode" | "decode") {
    setError(null);
    try {
      const next = mode === "encode" ? encodeUtf8(input) : decodeUtf8(input);
      setOutput(next);
      void record(mode);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Conversion failed");
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
          aria-label="Base64 input"
          className="min-h-[260px]"
        />
      </ToolPanel>
      <ToolPanel title="Output" actions={<ToolActions output={output} />}>
        <ToolError message={error} />
        <Textarea value={output} readOnly aria-label="Base64 output" className="mt-2 min-h-[260px]" />
      </ToolPanel>
    </div>
  );
}
