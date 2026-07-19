"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/ui/copy-button";
import { cn } from "@/lib/utils";

export function ToolPanel({
  title,
  children,
  className,
  actions,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
  actions?: ReactNode;
}) {
  return (
    <section className={cn("surface rounded-[var(--radius-lg)] p-4 sm:p-5", className)}>
      {(title || actions) && (
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          {title ? <h2 className="text-sm font-semibold">{title}</h2> : <span />}
          {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
        </div>
      )}
      {children}
    </section>
  );
}

export function ToolError({ message }: { message: string | null }) {
  const t = useTranslations("tool");
  if (!message) return null;
  return (
    <div
      className="rounded-[var(--radius-md)] border border-[var(--color-danger)]/40 bg-[color-mix(in_oklab,var(--color-danger)_12%,transparent)] px-3 py-2 text-sm text-[var(--color-danger)]"
      role="alert"
    >
      <span className="font-medium">{t("error")}: </span>
      {message}
    </div>
  );
}

export function ToolActions({
  onClear,
  output,
  children,
}: {
  onClear?: () => void;
  output?: string;
  children?: ReactNode;
}) {
  const t = useTranslations("tool");
  return (
    <div className="flex flex-wrap items-center gap-2">
      {children}
      {onClear ? (
        <Button type="button" variant="ghost" size="sm" onClick={onClear}>
          {t("clear")}
        </Button>
      ) : null}
      {output !== undefined && output !== "" ? (
        <CopyButton value={output} label={t("copy")} copiedLabel={t("copied")} />
      ) : null}
    </div>
  );
}
