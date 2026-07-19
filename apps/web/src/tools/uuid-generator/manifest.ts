import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "uuid-generator",
  slug: "uuid-generator",
  category: "developer",
  name: { en: "UUID Generator", ar: "مولّد UUID" },
  description: {
    en: "Generate RFC 4122 version 4 UUIDs in bulk.",
    ar: "أنشئ معرّفات UUID الإصدار 4 بكميات.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "in-tool",
  order: 3,
  seo: {
    title: { en: "UUID Generator Online", ar: "مولّد UUID أونلاين" },
    description: {
      en: "Generate secure random UUIDv4 values instantly in your browser.",
      ar: "أنشئ قيم UUIDv4 عشوائية فورًا في متصفحك.",
    },
    keywords: ["uuid", "guid", "uuid v4 generator"],
  },
};
