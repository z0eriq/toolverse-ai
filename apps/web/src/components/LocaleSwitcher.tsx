"use client";

import { useEffect, useState, useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { LOCALE_LABELS, locales, type AppLocale } from "@/i18n/routing";
import { LOCALE_CHOSEN_COOKIE } from "@/i18n/locale-preference";

/**
 * Locale select: update the control immediately, run navigation in a
 * transition so the interaction stays under INP budgets.
 */
export function LocaleSwitcher() {
  const t = useTranslations("nav");
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [displayLocale, setDisplayLocale] = useState(locale);

  useEffect(() => {
    setDisplayLocale(locale);
  }, [locale]);

  function markExplicitLocaleChoice() {
    // Remember that the user picked a language so middleware won't override
    // it with Accept-Language on the next visit.
    document.cookie = `${LOCALE_CHOSEN_COOKIE}=1; Path=/; Max-Age=31536000; SameSite=Lax`;
  }

  return (
    <>
      <label className="sr-only" htmlFor="locale-switcher">
        {t("language")}
      </label>
      <select
        id="locale-switcher"
        value={displayLocale}
        aria-label={t("language")}
        aria-busy={isPending}
        disabled={isPending}
        className="h-8 rounded-[var(--radius-md)] border border-transparent bg-transparent px-1.5 text-xs font-medium text-[var(--muted)] outline-none hover:text-[var(--foreground)] focus-visible:border-[var(--border)] disabled:opacity-60"
        onChange={(e) => {
          const next = e.target.value;
          // Synchronous UI update — lets the select paint before navigation work.
          setDisplayLocale(next);
          markExplicitLocaleChoice();
          startTransition(() => {
            router.replace(pathname, { locale: next });
          });
        }}
      >
        {locales.map((code) => (
          <option key={code} value={code}>
            {LOCALE_LABELS[code as AppLocale]}
          </option>
        ))}
      </select>
    </>
  );
}
