export type LocaleCode = "en" | "ar" | "es" | "fr" | "de" | "pt" | "zh";

export type LocalizedString = Partial<Record<LocaleCode, string>> & {
  en: string;
};

export type ToolCapability = "client" | "server" | "async";

export type AdSenseSlot = "in-tool" | "sidebar" | "none";

export type ToolCategoryId =
  | "developer"
  | "text"
  | "design"
  | "converters"
  | "security"
  | "ai"
  | "pdf"
  | "images"
  | "calculators";

export interface ToolSeo {
  title: LocalizedString;
  description?: LocalizedString;
  keywords: string[];
}

export interface ToolFaqItem {
  question: string;
  answer: string;
}

export interface ToolHowToStep {
  name: string;
  text: string;
}

export interface ToolManifest {
  /** Stable unique id, e.g. "json-formatter" */
  id: string;
  /** URL slug; usually same as id */
  slug: string;
  category: ToolCategoryId;
  name: LocalizedString;
  description: LocalizedString;
  version: string;
  premium?: boolean;
  adsenseSlot?: AdSenseSlot;
  seo: ToolSeo;
  schemaType?: "WebApplication" | "SoftwareApplication";
  capabilities: ToolCapability[];
  icon?: string;
  order?: number;
  /** Optional FAQ entries for JSON-LD */
  faq?: ToolFaqItem[];
  /** Optional HowTo steps for JSON-LD */
  howto?: ToolHowToStep[];
  howto_steps?: ToolHowToStep[];
}

export interface ToolFrontendModule {
  manifest: ToolManifest;
  /** Client component for the interactive tool UI */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Component: (props?: Record<string, never>) => any;
}

export const CATEGORY_META: Record<
  ToolCategoryId,
  { name: LocalizedString; description: LocalizedString; order: number }
> = {
  developer: {
    name: { en: "Developer", ar: "مطور" },
    description: {
      en: "JSON, encoding, hashing, JWT, and developer utilities",
      ar: "أدوات JSON والترميز والتجزئة وJWT للمطورين",
    },
    order: 1,
  },
  text: {
    name: { en: "Text", ar: "نص" },
    description: {
      en: "Writing helpers, counters, and markdown tools",
      ar: "أدوات الكتابة والعدادات وMarkdown",
    },
    order: 2,
  },
  design: {
    name: { en: "Design", ar: "تصميم" },
    description: {
      en: "Colors, contrast, and design utilities",
      ar: "الألوان والتباين وأدوات التصميم",
    },
    order: 3,
  },
  converters: {
    name: { en: "Converters", ar: "محولات" },
    description: {
      en: "Format and unit converters",
      ar: "محولات الصيغ والوحدات",
    },
    order: 4,
  },
  security: {
    name: { en: "Security", ar: "أمان" },
    description: {
      en: "Security and cryptography helpers",
      ar: "أدوات الأمان والتشفير",
    },
    order: 5,
  },
  ai: {
    name: { en: "AI", ar: "ذكاء اصطناعي" },
    description: {
      en: "AI-powered productivity tools",
      ar: "أدوات الإنتاجية المدعومة بالذكاء الاصطناعي",
    },
    order: 6,
  },
  pdf: {
    name: { en: "PDF", ar: "PDF" },
    description: {
      en: "PDF merge, split, compress, and convert utilities",
      ar: "دمج وتقسيم وضغط وتحويل ملفات PDF",
    },
    order: 7,
  },
  images: {
    name: { en: "Images", ar: "صور" },
    description: {
      en: "Image compress, resize, convert, and creative tools",
      ar: "ضغط وتغيير حجم وتحويل الصور وأدوات إبداعية",
    },
    order: 8,
  },
  calculators: {
    name: { en: "Calculators", ar: "حاسبات" },
    description: {
      en: "Finance, math, health, and unit calculators",
      ar: "حاسبات مالية ورياضية وصحية ووحدات",
    },
    order: 9,
  },
};
