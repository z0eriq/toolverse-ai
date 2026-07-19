import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function getSiteName(): string {
  return process.env.NEXT_PUBLIC_SITE_NAME ?? "ToolVerse AI";
}

export function getAppUrl(): string {
  return (process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000").replace(
    /\/$/,
    "",
  );
}

export function getApiUrl(): string {
  if (typeof window === "undefined") {
    return (
      process.env.API_INTERNAL_URL ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000/api/v1"
    ).replace(/\/$/, "");
  }
  return (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1").replace(
    /\/$/,
    "",
  );
}

export function isAdsEnabled(): boolean {
  return process.env.NEXT_PUBLIC_ADSENSE_ENABLED === "true";
}

export function localize(
  value: { en: string; ar?: string } | Record<string, string> | string | undefined,
  locale: string,
): string {
  if (!value) return "";
  if (typeof value === "string") return value;
  const keyed = value as Record<string, string>;
  if (keyed[locale]) return keyed[locale];
  if (keyed.en) return keyed.en;
  const first = Object.values(keyed)[0];
  return first ?? "";
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "absolute";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch {
      return false;
    }
  }
}
