import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "base64",
  slug: "base64",
  category: "developer",
  name: { en: "Base64 Encoder / Decoder", ar: "ترميز / فك Base64" },
  description: {
    en: "Encode text to Base64 or decode Base64 back to UTF-8 text.",
    ar: "رمّز النص إلى Base64 أو افكك Base64 إلى نص UTF-8.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "sidebar",
  order: 2,
  seo: {
    title: { en: "Base64 Encode Decode Online", ar: "ترميز وفك Base64 أونلاين" },
    description: {
      en: "Free Base64 encoder and decoder that runs entirely in your browser.",
      ar: "أداة ترميز وفك Base64 مجانية تعمل بالكامل في متصفحك.",
    },
    keywords: ["base64", "base64 encode", "base64 decode"],
  },
};
