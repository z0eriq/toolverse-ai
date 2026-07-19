"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Copy, Check, Linkedin, Share2, Twitter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { trackShareClick } from "@/lib/analytics";
import { cn, copyToClipboard, getAppUrl } from "@/lib/utils";

export function ShareBar({
  title,
  path,
  className,
}: {
  title?: string;
  /** Path without origin, e.g. `/tools/ai/slug`. Defaults to current pathname. */
  path?: string;
  className?: string;
}) {
  const t = useTranslations("share");
  const [copied, setCopied] = useState(false);

  const url =
    typeof window !== "undefined"
      ? path
        ? `${getAppUrl()}${path.startsWith("/") ? path : `/${path}`}`
        : window.location.href
      : path
        ? `${getAppUrl()}${path.startsWith("/") ? path : `/${path}`}`
        : getAppUrl();

  const shareTitle = title || t("defaultTitle");

  async function onNativeShare() {
    trackShareClick("native", path);
    if (typeof navigator !== "undefined" && navigator.share) {
      try {
        await navigator.share({ title: shareTitle, url });
        return;
      } catch {
        /* user cancelled or unsupported */
      }
    }
    await onCopy();
  }

  async function onCopy() {
    trackShareClick("copy", path);
    const ok = await copyToClipboard(url);
    if (ok) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    }
  }

  function onTwitter() {
    trackShareClick("twitter", path);
    const intent = new URL("https://twitter.com/intent/tweet");
    intent.searchParams.set("url", url);
    intent.searchParams.set("text", shareTitle);
    window.open(intent.toString(), "_blank", "noopener,noreferrer");
  }

  function onLinkedIn() {
    trackShareClick("linkedin", path);
    const intent = new URL("https://www.linkedin.com/sharing/share-offsite/");
    intent.searchParams.set("url", url);
    window.open(intent.toString(), "_blank", "noopener,noreferrer");
  }

  return (
    <div
      className={cn("flex flex-wrap items-center gap-2", className)}
      role="group"
      aria-label={t("label")}
    >
      <span className="text-xs uppercase tracking-wider text-[var(--muted)]">
        {t("label")}
      </span>
      <Button type="button" size="sm" variant="secondary" onClick={onNativeShare}>
        <Share2 className="h-3.5 w-3.5" aria-hidden />
        {t("share")}
      </Button>
      <Button type="button" size="sm" variant="ghost" onClick={onCopy}>
        {copied ? (
          <Check className="h-3.5 w-3.5" aria-hidden />
        ) : (
          <Copy className="h-3.5 w-3.5" aria-hidden />
        )}
        {copied ? t("copied") : t("copy")}
      </Button>
      <Button type="button" size="sm" variant="ghost" onClick={onTwitter} aria-label={t("twitter")}>
        <Twitter className="h-3.5 w-3.5" aria-hidden />
      </Button>
      <Button type="button" size="sm" variant="ghost" onClick={onLinkedIn} aria-label={t("linkedin")}>
        <Linkedin className="h-3.5 w-3.5" aria-hidden />
      </Button>
    </div>
  );
}
