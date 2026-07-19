"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Search } from "lucide-react";
import { getAllTools } from "@/tools/registry";
import { ToolCard } from "@/components/ToolCard";
import { Input } from "@/components/ui/input";
import { localize } from "@/lib/utils";
import { trackSearch } from "@/lib/analytics";

export function HomeSearch({
  initialCategory,
}: {
  initialCategory?: string;
}) {
  const t = useTranslations("home");
  const locale = useLocale();
  const [query, setQuery] = useState("");
  const tools = useMemo(() => getAllTools(), []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return tools.filter((tool) => {
      if (initialCategory && tool.manifest.category !== initialCategory) {
        return false;
      }
      if (!q) return true;
      const name = localize(tool.manifest.name, locale).toLowerCase();
      const desc = localize(tool.manifest.description, locale).toLowerCase();
      return (
        name.includes(q) ||
        desc.includes(q) ||
        tool.manifest.slug.includes(q) ||
        tool.manifest.category.includes(q)
      );
    });
  }, [tools, query, locale, initialCategory]);

  return (
    <section id="tools" className="scroll-mt-24">
      <div className="mb-6">
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {t("searchHeading")}
        </h2>
        <div className="relative mt-4 max-w-xl">
          <Search
            className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]"
            aria-hidden
          />
          <Input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (e.target.value.trim().length > 1) trackSearch(e.target.value.trim());
            }}
            placeholder={t("searchPlaceholder")}
            className="ps-10"
            aria-label={t("searchPlaceholder")}
          />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((tool, index) => (
          <ToolCard
            key={tool.manifest.id}
            slug={tool.manifest.slug}
            category={tool.manifest.category}
            name={tool.manifest.name}
            description={tool.manifest.description}
            locale={locale}
            premium={tool.manifest.premium}
            index={index}
          />
        ))}
      </div>
    </section>
  );
}
