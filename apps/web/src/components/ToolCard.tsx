"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowUpRight, Sparkles } from "lucide-react";
import { Link } from "@/i18n/navigation";
import { Badge } from "@/components/ui/badge";
import { localize } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { toolClick, toolImpression } from "@/lib/analytics";

export interface ToolCardProps {
  slug: string;
  category: string;
  name: { en: string; ar?: string } | Record<string, string> | string;
  description: { en: string; ar?: string } | Record<string, string> | string;
  locale: string;
  premium?: boolean;
  className?: string;
  index?: number;
  toolId?: string;
}

export function ToolCard({
  slug,
  category,
  name,
  description,
  locale,
  premium,
  className,
  index = 0,
  toolId,
}: ToolCardProps) {
  const title = localize(name, locale);
  const desc = localize(description, locale);
  const analyticsId = toolId || slug;

  useEffect(() => {
    toolImpression(analyticsId);
  }, [analyticsId]);

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.24) }}
    >
      <Link
        href={`/tools/${category}/${slug}`}
        className={cn(
          "group surface relative flex h-full flex-col rounded-[var(--radius-lg)] p-5 transition hover:border-[var(--accent)]/40 hover:shadow-[var(--shadow-glow)] focus-visible:outline-none",
          className,
        )}
        onClick={() => toolClick(analyticsId)}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)] bg-[color-mix(in_oklab,var(--accent)_14%,transparent)] text-[var(--accent)]">
            <Sparkles className="h-4 w-4" aria-hidden />
          </div>
          <ArrowUpRight
            className="h-4 w-4 text-[var(--muted)] transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-[var(--accent)]"
            aria-hidden
          />
        </div>
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <h3 className="font-display text-base font-semibold tracking-tight">{title}</h3>
          {premium ? <Badge>Premium</Badge> : null}
        </div>
        <p className="line-clamp-2 text-sm text-[var(--muted)]">{desc}</p>
        <span className="mt-4 text-xs uppercase tracking-wider text-[var(--muted)]">
          {category}
        </span>
      </Link>
    </motion.article>
  );
}
