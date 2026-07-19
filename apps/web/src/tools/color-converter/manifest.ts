import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "color-converter",
  slug: "color-converter",
  category: "design",
  name: { en: "Color Converter", ar: "محوّل الألوان" },
  description: {
    en: "Convert between HEX, RGB, and HSL color formats.",
    ar: "حوّل بين صيغ الألوان HEX وRGB وHSL.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "sidebar",
  order: 10,
  seo: {
    title: { en: "HEX RGB HSL Color Converter", ar: "محوّل ألوان HEX RGB HSL" },
    description: {
      en: "Convert colors between HEX, RGB, and HSL with a live preview.",
      ar: "حوّل الألوان بين HEX وRGB وHSL مع معاينة مباشرة.",
    },
    keywords: ["color converter", "hex to rgb", "hsl", "color picker"],
  },
};
