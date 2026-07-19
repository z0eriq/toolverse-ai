"use client";

import { useTranslations } from "next-intl";

export function SkipLink() {
  const t = useTranslations("skip");
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:fixed focus:start-4 focus:top-4 focus:z-[100] focus:rounded-[var(--radius-md)] focus:bg-[var(--accent)] focus:px-4 focus:py-2 focus:text-[var(--accent-fg)]"
    >
      {t("content")}
    </a>
  );
}
