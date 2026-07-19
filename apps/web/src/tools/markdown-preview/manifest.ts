import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "markdown-preview",
  slug: "markdown-preview",
  category: "text",
  name: { en: "Markdown Preview", ar: "معاينة Markdown" },
  description: {
    en: "Write Markdown and preview the rendered HTML side by side.",
    ar: "اكتب Markdown وعاين HTML المعروض جنبًا إلى جنب.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "sidebar",
  order: 8,
  seo: {
    title: { en: "Markdown Preview Online", ar: "معاينة Markdown أونلاين" },
    description: {
      en: "Live Markdown editor and preview that stays in your browser.",
      ar: "محرر ومعاينة Markdown مباشرة يبقيان في متصفحك.",
    },
    keywords: ["markdown", "md preview", "markdown editor"],
  },
};
