"use client";

import { useEffect, use } from "react";
import { useRouter } from "@/i18n/navigation";
import { api } from "@/lib/api";

/**
 * Landing for referral codes. Stores tv_ref cookie and sends visitors home.
 */
export default function ReferralLandingPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const { code } = use(params);
  const router = useRouter();

  useEffect(() => {
    const maxAge = 30 * 24 * 60 * 60;
    document.cookie = `tv_ref=${encodeURIComponent(code)}; path=/; max-age=${maxAge}; SameSite=Lax`;
    void api.referrals.resolve(code).catch(() => null);
    router.replace("/");
  }, [code, router]);

  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center text-sm text-[var(--muted)]">
      Applying referral…
    </div>
  );
}
