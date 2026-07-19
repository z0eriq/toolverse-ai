import { cn } from "@/lib/utils";

export function Badge({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[var(--radius-sm)] border border-[var(--border)] bg-[color-mix(in_oklab,var(--accent)_12%,transparent)] px-2 py-0.5 text-xs font-medium text-[var(--accent)]",
        className,
      )}
    >
      {children}
    </span>
  );
}
