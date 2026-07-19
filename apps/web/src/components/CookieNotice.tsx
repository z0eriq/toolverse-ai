"use client";

import { useEffect, useState } from "react";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";

const STORAGE_KEY = "tv_cookie_notice_v1";

/**
 * Lightweight privacy notice for analytics/cookies (AdSense readiness).
 * Does not load ads — only informs and links to the privacy policy.
 */
export function CookieNotice() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(STORAGE_KEY)) setOpen(true);
    } catch {
      setOpen(true);
    }
  }, []);

  function dismiss() {
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      /* ignore */
    }
    setOpen(false);
  }

  if (!open) return null;

  return (
    <div
      className="fixed inset-x-0 bottom-0 z-[55] border-t border-[var(--border)] bg-[var(--card)] p-4 shadow-lg"
      role="dialog"
      aria-label="Cookie and privacy notice"
    >
      <div className="mx-auto flex max-w-6xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-[var(--muted)]">
          We use essential cookies and may use analytics or advertising cookies
          when enabled. See our{" "}
          <Link href="/privacy" className="text-[var(--accent)] underline-offset-2 hover:underline">
            Privacy Policy
          </Link>
          .
        </p>
        <Button type="button" size="sm" onClick={dismiss}>
          Got it
        </Button>
      </div>
    </div>
  );
}
