import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "hash-generator",
  slug: "hash-generator",
  category: "security",
  name: { en: "Hash Generator", ar: "مولّد التجزئة" },
  description: {
    en: "Compute SHA-1, SHA-256, and SHA-512 hashes in the browser.",
    ar: "احسب تجزئات SHA-1 وSHA-256 وSHA-512 في المتصفح.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "sidebar",
  order: 4,
  seo: {
    title: { en: "SHA Hash Generator", ar: "مولّد تجزئة SHA" },
    description: {
      en: "Generate SHA hashes from text without sending data to a server.",
      ar: "أنشئ تجزئات SHA من النص دون إرسال البيانات إلى خادم.",
    },
    keywords: ["sha256", "sha512", "hash generator", "checksum"],
  },
};
