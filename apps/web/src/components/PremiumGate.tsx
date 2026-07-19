"use client";

import Link from "next/link";
import { useLocale } from "next-intl";
import { useAuth } from "@/features/auth/auth-context";

interface PremiumGateProps {
  premium?: boolean;
  /** When true, show upgrade CTA for limit / Pro messaging (e.g. after 429). */
  limitExceeded?: boolean;
  children: React.ReactNode;
}

export function PremiumGate({
  premium = false,
  limitExceeded = false,
  children,
}: PremiumGateProps) {
  const { user, isLoading } = useAuth();
  const locale = useLocale();

  if (!premium && !limitExceeded) {
    return <>{children}</>;
  }

  if (isLoading) {
    return (
      <div
        className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center text-sm text-[var(--muted)]"
        role="status"
        aria-live="polite"
      >
        Checking subscription…
      </div>
    );
  }

  if (!limitExceeded && user?.is_premium) {
    return <>{children}</>;
  }

  return (
    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)]">
      {!limitExceeded ? (
        <div
          className="pointer-events-none select-none blur-[2px] opacity-40"
          aria-hidden
        >
          {children}
        </div>
      ) : null}
      <div
        className={
          limitExceeded
            ? "flex items-center justify-center p-6"
            : "absolute inset-0 flex items-center justify-center bg-[color-mix(in_oklab,var(--bg)_72%,transparent)] p-6 backdrop-blur-sm"
        }
      >
        <div className="max-w-md rounded-2xl border border-[var(--border)] bg-[var(--bg)] p-6 text-center shadow-lg">
          <p className="text-xs font-medium uppercase tracking-wider text-[var(--accent)]">
            Pro
          </p>
          <h2 className="mt-2 font-display text-xl font-semibold">
            {limitExceeded
              ? "You’ve hit the Free plan limit"
              : "Unlock this tool with Pro"}
          </h2>
          <p className="mt-2 text-sm text-[var(--muted)]">
            {limitExceeded
              ? "Upgrade to Pro for unlimited tool runs, no ads, and higher API quotas."
              : "Pro removes ads, raises API limits, and unlocks advanced tools."}
          </p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
            <Link
              href={`/${locale}/pricing`}
              className="inline-flex h-10 items-center justify-center rounded-full bg-[var(--accent)] px-5 text-sm font-medium text-[var(--accent-fg)] transition hover:opacity-90"
            >
              View Pro plans
            </Link>
            {!user ? (
              <Link
                href={`/${locale}/auth/login`}
                className="inline-flex h-10 items-center justify-center rounded-full border border-[var(--border)] px-5 text-sm font-medium transition hover:bg-[var(--surface)]"
              >
                Sign in
              </Link>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
