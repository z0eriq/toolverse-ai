import type { ToolManifest } from "@toolverse/tool-sdk";

export const manifest: ToolManifest = {
  id: "url-encoder",
  slug: "url-encoder",
  category: "developer",
  name: { en: "URL Encoder / Decoder", ar: "ترميز / فك عنوان URL" },
  description: {
    en: "Encode or decode URL components safely.",
    ar: "رمّز أو افكك مكوّنات عنوان URL بأمان.",
  },
  version: "1.0.0",
  capabilities: ["client"],
  adsenseSlot: "sidebar",
  order: 5,
  seo: {
    title: { en: "URL Encode Decode Tool", ar: "أداة ترميز وفك URL" },
    description: {
      en: "Percent-encode and decode URLs and query strings in your browser.",
      ar: "رمّز وافكك عناوين URL وسلاسل الاستعلام في متصفحك.",
    },
    keywords: ["url encode", "url decode", "percent encoding"],
  },
};
