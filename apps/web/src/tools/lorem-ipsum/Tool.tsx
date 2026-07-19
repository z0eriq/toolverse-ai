"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ToolActions, ToolError, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

const WORDS = [
  "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
  "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
  "magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
  "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
  "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
  "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
  "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
  "deserunt", "mollit", "anim", "id", "est", "laborum",
];

function paragraph(): string {
  const len = 40 + Math.floor(Math.random() * 40);
  const words: string[] = [];
  for (let i = 0; i < len; i += 1) {
    const w = WORDS[Math.floor(Math.random() * WORDS.length)] ?? "lorem";
    words.push(i === 0 ? w.charAt(0).toUpperCase() + w.slice(1) : w);
  }
  return `${words.join(" ")}.`;
}

export function Tool() {
  const [count, setCount] = useState(3);
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { record } = useToolHistory(manifest.id);

  function generate() {
    setError(null);
    try {
      const n = Math.min(20, Math.max(1, Math.floor(count) || 1));
      const text = Array.from({ length: n }, () => paragraph()).join("\n\n");
      setOutput(text);
      void record("generate", { paragraphs: n });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    }
  }

  return (
    <ToolPanel
      title="Lorem Ipsum"
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
        <Label htmlFor="paragraphs">Paragraphs (1–20)</Label>
        <Input
          id="paragraphs"
          type="number"
          min={1}
          max={20}
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
        />
      </div>
      <ToolError message={error} />
      <Textarea
        value={output}
        readOnly
        aria-label="Generated lorem ipsum"
        className="mt-2 min-h-[280px]"
        placeholder="Click Generate"
      />
    </ToolPanel>
  );
}
