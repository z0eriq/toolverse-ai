import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Textarea({
  className,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "flex min-h-[120px] w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--card)] px-3 py-2 font-mono text-sm text-[var(--foreground)] placeholder:text-[var(--muted)] transition focus-visible:border-[var(--ring)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]/30 disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}
