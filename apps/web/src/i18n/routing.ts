import { defineRouting } from "next-intl/routing";

export const locales = ["en", "ar", "es", "fr", "de", "pt", "zh"] as const;
export type AppLocale = (typeof locales)[number];

export const routing = defineRouting({
  locales,
  defaultLocale: "en",
  localePrefix: "as-needed",
  // Match browser/device language (Accept-Language) on first visit.
  localeDetection: true,
});

export const RTL_LOCALES = new Set<AppLocale>(["ar"]);

export function isRtlLocale(locale: string): boolean {
  return RTL_LOCALES.has(locale as AppLocale);
}

export const LOCALE_OG_MAP: Record<AppLocale, string> = {
  en: "en_US",
  ar: "ar_SA",
  es: "es_ES",
  fr: "fr_FR",
  de: "de_DE",
  pt: "pt_BR",
  zh: "zh_CN",
};

export const LOCALE_LABELS: Record<AppLocale, string> = {
  en: "EN",
  ar: "عربي",
  es: "ES",
  fr: "FR",
  de: "DE",
  pt: "PT",
  zh: "中文",
};
