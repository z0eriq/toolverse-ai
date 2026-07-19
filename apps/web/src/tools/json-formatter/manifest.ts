import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "json-formatter",
  slug: "json-formatter",
  category: "developer",
  name: { en: "JSON Formatter", ar: "منسق JSON" },
  description: {
    en: "Format, minify, and validate JSON with clear error messages.",
    ar: "نسّق واصغر وتحقق من JSON مع رسائل خطأ واضحة.",
  },
  version: "1.0.0",
  premium: false,
  adsenseSlot: "sidebar",
  capabilities: ["client"],
  icon: "braces",
  order: 1,
  seo: {
    title: { en: "JSON Formatter & Validator", ar: "منسق ومدقق JSON" },
    description: {
      en: "Beautify or minify JSON online. Free, private, runs in your browser.",
      ar: "جمّل أو صغّر JSON عبر الإنترنت. مجاني وخاص ويعمل في متصفحك.",
    },
    keywords: ["json formatter", "json beautify", "json minify", "json validator"],
  },
  schemaType: "WebApplication",
};
