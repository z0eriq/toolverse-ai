import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "jwt-decoder",
  slug: "jwt-decoder",
  category: "security",
  name: { en: "JWT Decoder", ar: "مفكك JWT" },
  description: {
    en: "Decode JWT header and payload without verifying signatures.",
    ar: "افكك ترويسة وحمولة JWT دون التحقق من التوقيع.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "sidebar",
  order: 6,
  seo: {
    title: { en: "JWT Decoder Online", ar: "مفكك JWT أونلاين" },
    description: {
      en: "Inspect JWT claims locally. Nothing is uploaded.",
      ar: "افحص مطالبات JWT محليًا. لا يُرفع شيء.",
    },
    keywords: ["jwt", "jwt decoder", "json web token"],
  },
};
