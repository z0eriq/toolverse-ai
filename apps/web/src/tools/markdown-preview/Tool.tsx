"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Textarea } from "@/components/ui/textarea";
import { ToolActions, ToolPanel } from "@/components/ui/tool-panel";
import { useToolHistory } from "@/lib/use-tool-history";
import { manifest } from "./manifest";

const SAMPLE = `# ToolVerse Markdown

Write **bold**, _italic_, and \`code\`.

- Lists
- Work great

\`\`\`ts
const hello = "world";
\`\`\`
`;

export function Tool() {
  const [input, setInput] = useState(SAMPLE);
  const { record } = useToolHistory(manifest.id);

  useEffect(() => {
    const id = window.setTimeout(() => {
      if (input.trim()) void record("preview", { length: input.length });
    }, 1200);
    return () => window.clearTimeout(id);
  }, [input, record]);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ToolPanel
        title="Markdown"
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
          aria-label="Markdown input"
          className="min-h-[360px]"
        />
      </ToolPanel>
      <ToolPanel title="Preview">
        <article className="prose-tool min-h-[360px] max-w-none space-y-3 text-sm leading-relaxed [&_code]:rounded [&_code]:bg-[color-mix(in_oklab,var(--accent)_12%,transparent)] [&_code]:px-1 [&_h1]:font-display [&_h1]:text-2xl [&_h1]:font-semibold [&_h2]:text-xl [&_h2]:font-semibold [&_pre]:overflow-auto [&_pre]:rounded-[var(--radius-md)] [&_pre]:border [&_pre]:border-[var(--border)] [&_pre]:bg-[var(--background)] [&_pre]:p-3 [&_ul]:list-disc [&_ul]:ps-5">
          <ReactMarkdown>{input}</ReactMarkdown>
        </article>
      </ToolPanel>
    </div>
  );
}
