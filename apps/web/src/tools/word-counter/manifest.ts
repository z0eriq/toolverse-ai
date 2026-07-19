import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "word-counter",
  slug: "word-counter",
  category: "text",
  name: { en: "Word Counter", ar: "عداد الكلمات" },
  description: {
    en: "Count words, characters, sentences, and reading time.",
    ar: "عدّ الكلمات والأحرف والجمل ووقت القراءة.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "in-tool",
  order: 9,
  seo: {
    title: { en: "Word Counter Online", ar: "عداد الكلمات أونلاين" },
    description: {
      en: "Instant word and character counts for essays, posts, and scripts.",
      ar: "عدّ فوري للكلمات والأحرف للمقالات والمنشورات والنصوص.",
    },
    keywords: ["word counter", "character count", "reading time"],
  },
};
