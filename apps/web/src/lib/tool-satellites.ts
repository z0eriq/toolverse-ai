/**
 * Programmatic SEO satellite pages for every tool.
 * Content is generated from tool metadata (AI Content Factory enriches later).
 */

import type { ToolManifest } from "@toolverse/tool-sdk";
import type { ToolDetail, ToolFaqItem, ToolHowToStep, ToolListItem } from "@/lib/api";
import { localize } from "@/lib/utils";
import { buildPageMetadata } from "@/lib/seo";
import type { Metadata } from "next";

export const SATELLITE_KINDS = [
  "howto",
  "faq",
  "examples",
  "alternatives",
  "api",
  "use-cases",
  "changelog",
] as const;

export type SatelliteKind = (typeof SATELLITE_KINDS)[number];

export function isSatelliteKind(value: string): value is SatelliteKind {
  return (SATELLITE_KINDS as readonly string[]).includes(value);
}

export function satellitePath(
  category: string,
  slug: string,
  kind: SatelliteKind,
): string {
  return `/tools/${category}/${slug}/${kind}`;
}

export function toolBasePath(category: string, slug: string): string {
  return `/tools/${category}/${slug}`;
}

const LABELS: Record<
  SatelliteKind,
  { en: string; ar: string; es: string; fr: string; de: string; pt: string; zh: string }
> = {
  howto: {
    en: "How to use",
    ar: "كيفية الاستخدام",
    es: "Cómo usar",
    fr: "Comment utiliser",
    de: "Anleitung",
    pt: "Como usar",
    zh: "使用方法",
  },
  faq: {
    en: "FAQ",
    ar: "الأسئلة الشائعة",
    es: "Preguntas frecuentes",
    fr: "FAQ",
    de: "FAQ",
    pt: "Perguntas frequentes",
    zh: "常见问题",
  },
  examples: {
    en: "Examples",
    ar: "أمثلة",
    es: "Ejemplos",
    fr: "Exemples",
    de: "Beispiele",
    pt: "Exemplos",
    zh: "示例",
  },
  alternatives: {
    en: "Alternatives",
    ar: "بدائل",
    es: "Alternativas",
    fr: "Alternatives",
    de: "Alternativen",
    pt: "Alternativas",
    zh: "替代方案",
  },
  api: {
    en: "API documentation",
    ar: "توثيق API",
    es: "Documentación API",
    fr: "Documentation API",
    de: "API-Dokumentation",
    pt: "Documentação da API",
    zh: "API 文档",
  },
  "use-cases": {
    en: "Use cases",
    ar: "حالات الاستخدام",
    es: "Casos de uso",
    fr: "Cas d'usage",
    de: "Anwendungsfälle",
    pt: "Casos de uso",
    zh: "使用场景",
  },
  changelog: {
    en: "Changelog",
    ar: "سجل التغييرات",
    es: "Registro de cambios",
    fr: "Journal des modifications",
    de: "Änderungsprotokoll",
    pt: "Registro de alterações",
    zh: "更新日志",
  },
};

export function satelliteLabel(kind: SatelliteKind, locale: string): string {
  const row = LABELS[kind];
  return (row as Record<string, string>)[locale] ?? row.en;
}

export interface ToolSeoContext {
  slug: string;
  category: string;
  name: string;
  description: string;
  toolId: string;
  version: string;
  premium: boolean;
  faq: ToolFaqItem[];
  howto: ToolHowToStep[];
  capabilities: string[];
  related: ToolListItem[];
}

export function buildToolSeoContext(
  locale: string,
  manifest: ToolManifest | null,
  apiTool: ToolDetail | null,
  related: ToolListItem[] = [],
): ToolSeoContext | null {
  const slug = apiTool?.slug ?? manifest?.slug;
  const category = apiTool?.category ?? manifest?.category;
  if (!slug || !category) return null;

  const name = localize(
    (apiTool?.name as Record<string, string>) ?? manifest?.name,
    locale,
  );
  const description = localize(
    (apiTool?.description as Record<string, string>) ?? manifest?.description,
    locale,
  );

  const faq =
    (apiTool?.faq?.length ? apiTool.faq : manifest?.faq) ??
    defaultFaqs(name, locale);
  const howto =
    (apiTool?.howto_steps?.length
      ? apiTool.howto_steps
      : manifest?.howto ?? manifest?.howto_steps) ?? defaultHowTo(name, locale);

  return {
    slug,
    category,
    name,
    description,
    toolId: apiTool?.tool_id ?? manifest?.id ?? slug,
    version: apiTool?.version ?? manifest?.version ?? "1.0.0",
    premium: Boolean(apiTool?.premium ?? manifest?.premium),
    faq: faq.filter((f) => f?.question && f?.answer),
    howto: howto.filter((s) => s?.name && s?.text),
    capabilities: (apiTool?.capabilities ?? manifest?.capabilities ?? []) as string[],
    related,
  };
}

function defaultFaqs(name: string, locale: string): ToolFaqItem[] {
  if (locale === "ar") {
    return [
      {
        question: `ما هو ${name}؟`,
        answer: `${name} أداة مجانية عبر الإنترنت من ToolVerse AI تساعدك على إنجاز المهمة بسرعة في المتصفح.`,
      },
      {
        question: "هل أحتاج إلى إنشاء حساب؟",
        answer: "يمكنك استخدام معظم الأدوات مجانًا دون تسجيل. الحساب يحفظ المفضلة والسجل.",
      },
      {
        question: "هل بياناتي آمنة؟",
        answer: "تتم المعالجة في المتصفح كلما أمكن. لا نخزن مدخلاتك إلا إذا حفظتها أنت في مساحة العمل.",
      },
    ];
  }
  return [
    {
      question: `What is ${name}?`,
      answer: `${name} is a free online ToolVerse AI utility that helps you complete the task instantly in your browser.`,
    },
    {
      question: "Do I need an account?",
      answer:
        "Most tools work without signing in. An account unlocks favorites, history, and saved outputs.",
    },
    {
      question: "Is my data private?",
      answer:
        "Processing happens in the browser whenever possible. We do not store your inputs unless you save them to your workspace.",
    },
  ];
}

function defaultHowTo(name: string, locale: string): ToolHowToStep[] {
  if (locale === "ar") {
    return [
      { name: "افتح الأداة", text: `انتقل إلى صفحة ${name} على ToolVerse AI.` },
      { name: "أدخل البيانات", text: "الصق أو اكتب المدخلات في الحقول المتاحة." },
      { name: "شغّل الأداة", text: "اضغط الزر الرئيسي لمعالجة المحتوى فورًا." },
      { name: "انسخ النتيجة", text: "انسخ الناتج أو احفظه في مساحة العمل." },
    ];
  }
  return [
    { name: "Open the tool", text: `Go to the ${name} page on ToolVerse AI.` },
    { name: "Enter your input", text: "Paste or type your data into the available fields." },
    { name: "Run the tool", text: "Click the primary action to process your content instantly." },
    { name: "Copy the result", text: "Copy the output or save it to your workspace." },
  ];
}

export function satelliteMetadata(
  ctx: ToolSeoContext,
  kind: SatelliteKind,
  locale: string,
): Metadata {
  const label = satelliteLabel(kind, locale);
  const title = `${ctx.name} — ${label}`;
  const description = `${label} for ${ctx.name}. ${ctx.description}`.slice(0, 160);
  return buildPageMetadata({
    title,
    description,
    path: satellitePath(ctx.category, ctx.slug, kind),
    locale,
    keywords: [ctx.name, label, ctx.category, "online tool", "free"],
  });
}

export interface SatelliteSection {
  heading: string;
  body: string;
  bullets?: string[];
  code?: string;
}

export function buildSatelliteContent(
  ctx: ToolSeoContext,
  kind: SatelliteKind,
  locale: string,
): { title: string; intro: string; sections: SatelliteSection[] } {
  const label = satelliteLabel(kind, locale);
  const title = `${ctx.name}: ${label}`;

  switch (kind) {
    case "howto":
      return {
        title,
        intro:
          locale === "ar"
            ? `دليل خطوة بخطوة لاستخدام ${ctx.name} مجانًا عبر الإنترنت.`
            : `A step-by-step guide to using ${ctx.name} free online.`,
        sections: ctx.howto.map((step) => ({
          heading: step.name,
          body: step.text,
        })),
      };
    case "faq":
      return {
        title,
        intro:
          locale === "ar"
            ? `إجابات شائعة حول ${ctx.name}.`
            : `Common questions and answers about ${ctx.name}.`,
        sections: ctx.faq.map((item) => ({
          heading: item.question,
          body: item.answer,
        })),
      };
    case "examples":
      return {
        title,
        intro:
          locale === "ar"
            ? `أمثلة عملية توضح كيف يساعدك ${ctx.name}.`
            : `Practical examples showing how ${ctx.name} helps you work faster.`,
        sections: [
          {
            heading: locale === "ar" ? "مثال سريع" : "Quick example",
            body:
              locale === "ar"
                ? `استخدم ${ctx.name} لتحويل المدخلات إلى نتيجة جاهزة للنشر أو التطوير.`
                : `Use ${ctx.name} to turn raw input into a ready-to-ship result for development or publishing.`,
            bullets: [
              locale === "ar" ? "الصق المحتوى" : "Paste sample content",
              locale === "ar" ? "اضغط تشغيل" : "Click run",
              locale === "ar" ? "راجع الناتج" : "Review the output",
            ],
          },
          {
            heading: locale === "ar" ? "سيناريو احترافي" : "Professional workflow",
            body:
              locale === "ar"
                ? "ادمج الأداة في روتينك اليومي مع المفضلة والسجل."
                : "Combine this tool with favorites and history for a repeatable daily workflow.",
          },
        ],
      };
    case "alternatives":
      return {
        title,
        intro:
          locale === "ar"
            ? `بدائل وأدوات ذات صلة بـ ${ctx.name} على ToolVerse AI.`
            : `Related tools and alternatives to ${ctx.name} on ToolVerse AI.`,
        sections: [
          {
            heading: locale === "ar" ? "أدوات مشابهة" : "Similar tools",
            body:
              locale === "ar"
                ? "استكشف أدوات في نفس الفئة أو مهام متجاورة."
                : "Explore tools in the same category or adjacent workflows.",
            bullets: ctx.related.slice(0, 6).map((t) => {
              const n =
                typeof t.name === "string"
                  ? t.name
                  : localize(t.name as Record<string, string>, locale);
              return n;
            }),
          },
        ],
      };
    case "api":
      return {
        title,
        intro:
          locale === "ar"
            ? `استخدم ${ctx.name} برمجيًا عبر واجهة ToolVerse REST API.`
            : `Use ${ctx.name} programmatically via the ToolVerse REST API.`,
        sections: [
          {
            heading: "Endpoint",
            body: `POST /api/v1/t/${ctx.toolId.replace(/^dynamic:/, "")}/`,
            code: `curl -X POST "$API/t/${ctx.slug}/" \\\n  -H "X-API-Key: tv_xxx" \\\n  -H "Content-Type: application/json" \\\n  -d '{"input":"..."}'`,
          },
          {
            heading: locale === "ar" ? "المصادقة" : "Authentication",
            body:
              locale === "ar"
                ? "استخدم مفتاح API من بوابة المطورين أو رمز JWT للمستخدم."
                : "Authenticate with an API key from the Developers portal or a user JWT.",
          },
          {
            heading: locale === "ar" ? "القدرات" : "Capabilities",
            body: (ctx.capabilities.length ? ctx.capabilities : ["client", "server"]).join(", "),
          },
        ],
      };
    case "use-cases":
      return {
        title,
        intro:
          locale === "ar"
            ? `حالات استخدام شائعة لـ ${ctx.name}.`
            : `Popular use cases for ${ctx.name}.`,
        sections: [
          {
            heading: locale === "ar" ? "للمطورين" : "For developers",
            body:
              locale === "ar"
                ? "سرّع مهام التطوير اليومية دون تثبيت برامج."
                : "Speed up daily engineering tasks without installing desktop software.",
          },
          {
            heading: locale === "ar" ? "للفرق" : "For teams",
            body:
              locale === "ar"
                ? "وحّد سير العمل عبر رابط واحد قابل للمشاركة."
                : "Standardize workflows with a single shareable browser link.",
          },
          {
            heading: locale === "ar" ? "للتعلم" : "For learning",
            body:
              locale === "ar"
                ? "جرّب المفاهيم بسرعة مع ملاحظات فورية."
                : "Experiment and learn with instant feedback on real inputs.",
          },
        ],
      };
    case "changelog":
      return {
        title,
        intro:
          locale === "ar"
            ? `سجل إصدارات ${ctx.name}.`
            : `Release history for ${ctx.name}.`,
        sections: [
          {
            heading: `v${ctx.version}`,
            body:
              locale === "ar"
                ? "الإصدار الحالي على ToolVerse AI مع تحسينات الأداء وإمكانية الوصول."
                : "Current release on ToolVerse AI with performance and accessibility improvements.",
            bullets: [
              locale === "ar" ? "واجهة متجاوبة" : "Responsive UI",
              locale === "ar" ? "تحسينات SEO" : "SEO enhancements",
              locale === "ar" ? "دعم المفضلة والسجل" : "Favorites and history support",
            ],
          },
        ],
      };
    default:
      return { title, intro: ctx.description, sections: [] };
  }
}

/** All URL paths for one tool (main + satellites) for sitemap generation. */
export function allToolSeoPaths(category: string, slug: string): string[] {
  return [
    toolBasePath(category, slug),
    ...SATELLITE_KINDS.map((kind) => satellitePath(category, slug, kind)),
  ];
}
