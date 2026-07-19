"use client";

import { motion } from "framer-motion";
import { CATEGORY_META, type ToolCategoryId } from "@toolverse/tool-sdk";
import { Link } from "@/i18n/navigation";
import { localize } from "@/lib/utils";
import { useTranslations } from "next-intl";

const categoryIds = Object.keys(CATEGORY_META) as ToolCategoryId[];

export function CategoryGrid({ locale }: { locale: string }) {
  const t = useTranslations("common");

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {categoryIds.map((id, index) => {
        const meta = CATEGORY_META[id];
        return (
          <motion.div
            key={id}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.05, duration: 0.35 }}
          >
            <Link
              href={`/?category=${id}#tools`}
              className="surface group block rounded-[var(--radius-lg)] p-5 transition hover:border-[var(--accent)]/40"
            >
              <h3 className="font-display text-lg font-semibold tracking-tight group-hover:text-[var(--accent)]">
                {localize(meta.name, locale)}
              </h3>
              <p className="mt-2 text-sm text-[var(--muted)]">
                {localize(meta.description, locale)}
              </p>
              <span className="mt-4 inline-block text-xs uppercase tracking-wider text-[var(--accent)]">
                {t("open")} →
              </span>
            </Link>
          </motion.div>
        );
      })}
    </div>
  );
}
