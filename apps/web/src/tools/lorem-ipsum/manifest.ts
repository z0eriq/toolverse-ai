import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "lorem-ipsum",
  slug: "lorem-ipsum",
  category: "text",
  name: { en: "Lorem Ipsum Generator", ar: "مولّد لوريم إيبسوم" },
  description: {
    en: "Generate placeholder paragraphs for layouts and mockups.",
    ar: "أنشئ فقرات نائبة للتخطيطات والنماذج.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "in-tool",
  order: 7,
  seo: {
    title: { en: "Lorem Ipsum Generator", ar: "مولّد لوريم إيبسوم" },
    description: {
      en: "Create custom-length lorem ipsum text instantly.",
      ar: "أنشئ نص لوريم إيبسوم بطول مخصص فورًا.",
    },
    keywords: ["lorem ipsum", "placeholder text", "dummy text"],
  },
};
