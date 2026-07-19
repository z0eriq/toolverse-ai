"use client";

import { useEffect, useMemo, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { ToolActions, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

function analyze(text: string) {
  const trimmed = text.trim();
  const words = trimmed ? trimmed.split(/\s+/).filter(Boolean).length : 0;
  const chars = text.length;
  const charsNoSpaces = text.replace(/\s/g, "").length;
  const sentences = trimmed
    ? trimmed.split(/[.!?]+/).filter((s) => s.trim().length > 0).length
    : 0;
  const paragraphs = trimmed
    ? trimmed.split(/\n\s*\n/).filter((p) => p.trim().length > 0).length
    : 0;
  const readingMinutes = Math.max(1, Math.ceil(words / 200));
  return { words, chars, charsNoSpaces, sentences, paragraphs, readingMinutes };
}

export function Tool() {
  const [input, setInput] = useState(
    "ToolVerse AI helps you ship faster with free, beautiful online tools.",
  );
  const stats = useMemo(() => analyze(input), [input]);
  const { record } = useToolHistory(manifest.id);

  useEffect(() => {
    const id = window.setTimeout(() => {
      if (input.trim()) void record("count", stats);
    }, 1500);
    return () => window.clearTimeout(id);
  }, [input, record, stats]);

  const cards = [
    { label: "Words", value: stats.words },
    { label: "Characters", value: stats.chars },
    { label: "Characters (no spaces)", value: stats.charsNoSpaces },
    { label: "Sentences", value: stats.sentences },
    { label: "Paragraphs", value: stats.paragraphs },
    { label: "Reading time", value: `${stats.readingMinutes} min` },
  ];

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.label} className="surface rounded-[var(--radius-lg)] p-4">
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">{card.label}</p>
            <p className="mt-1 font-display text-2xl font-semibold tabular-nums">{card.value}</p>
          </div>
        ))}
      </div>
      <ToolPanel
        title="Text"
        actions={
          <ToolActions
            output={input}
            onClear={() => setInput("")}
          />
        }
      >
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Text to count"
          className="min-h-[280px]"
        />
      </ToolPanel>
    </div>
  );
}
