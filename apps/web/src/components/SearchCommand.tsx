"use client";

import { useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Search, X } from "lucide-react";
import { getAllTools } from "@/tools/registry";
import { Link } from "@/i18n/navigation";
import { localize } from "@/lib/utils";
import { trackSearch } from "@/lib/analytics";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function SearchCommand({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const t = useTranslations("nav");
  const locale = useLocale();
  const [query, setQuery] = useState("");
  const tools = useMemo(() => getAllTools(), []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onOpenChange(true);
      }
      if (e.key === "Escape") onOpenChange(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onOpenChange]);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return tools.slice(0, 8);
    return tools
      .filter((tool) => {
        const name = localize(tool.manifest.name, locale).toLowerCase();
        const desc = localize(tool.manifest.description, locale).toLowerCase();
        return (
          name.includes(q) ||
          desc.includes(q) ||
          tool.manifest.slug.includes(q) ||
          tool.manifest.seo.keywords.some((k) => k.toLowerCase().includes(q))
        );
      })
      .slice(0, 12);
  }, [query, tools, locale]);

  useEffect(() => {
    if (query.trim().length > 1) trackSearch(query.trim());
  }, [query]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[80] flex items-start justify-center bg-black/55 p-4 pt-[12vh] backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={t("search")}
      onClick={() => onOpenChange(false)}
    >
      <div
        className="surface w-full max-w-xl overflow-hidden rounded-[var(--radius-lg)] shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-[var(--border)] px-3">
          <Search className="h-4 w-4 shrink-0 text-[var(--muted)]" aria-hidden />
          <Input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("search")}
            className="border-0 bg-transparent shadow-none focus-visible:ring-0"
            aria-label={t("search")}
          />
          <Button type="button" variant="ghost" size="icon" onClick={() => onOpenChange(false)} aria-label="Close">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <ul className="max-h-[50vh] overflow-auto p-2" role="listbox">
          {results.map((tool) => (
            <li key={tool.manifest.id}>
              <Link
                href={`/tools/${tool.manifest.category}/${tool.manifest.slug}`}
                className="block rounded-[var(--radius-md)] px-3 py-2.5 hover:bg-[color-mix(in_oklab,var(--accent)_10%,transparent)]"
                onClick={() => onOpenChange(false)}
              >
                <p className="text-sm font-medium">
                  {localize(tool.manifest.name, locale)}
                </p>
                <p className="line-clamp-1 text-xs text-[var(--muted)]">
                  {localize(tool.manifest.description, locale)}
                </p>
              </Link>
            </li>
          ))}
          {results.length === 0 ? (
            <li className="px-3 py-6 text-center text-sm text-[var(--muted)]">No tools found</li>
          ) : null}
        </ul>
      </div>
    </div>
  );
}
