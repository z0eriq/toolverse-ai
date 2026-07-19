"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { copyToClipboard } from "@/lib/utils";

export function CopyButton({
  value,
  label = "Copy",
  copiedLabel = "Copied",
  className,
}: {
  value: string;
  label?: string;
  copiedLabel?: string;
  className?: string;
}) {
  const [copied, setCopied] = useState(false);

  async function onCopy() {
    const ok = await copyToClipboard(value);
    if (!ok) return;
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <Button
      type="button"
      variant="secondary"
      size="sm"
      className={className}
      onClick={() => void onCopy()}
      aria-label={copied ? copiedLabel : label}
    >
      {copied ? <Check className="h-4 w-4" aria-hidden /> : <Copy className="h-4 w-4" aria-hidden />}
      {copied ? copiedLabel : label}
    </Button>
  );
}
