"use client";

import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

export function GamificationReferralStrip() {
  const queryClient = useQueryClient();
  const [claimCode, setClaimCode] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  const points = useQuery({
    queryKey: ["gamification-me"],
    queryFn: () => api.gamification.me(),
    retry: false,
  });

  const referral = useQuery({
    queryKey: ["referrals-me"],
    queryFn: () => api.referrals.me(),
    retry: false,
  });

  const claim = useMutation({
    mutationFn: () => api.referrals.claim(claimCode.trim()),
    onSuccess: async () => {
      setMsg("Referral claimed.");
      setClaimCode("");
      await queryClient.invalidateQueries({ queryKey: ["referrals-me"] });
      await queryClient.invalidateQueries({ queryKey: ["gamification-me"] });
    },
    onError: (err) => {
      setMsg(err instanceof ApiError ? err.message : "Could not claim code");
    },
  });

  const shareUrl = useMemo(() => {
    if (typeof window === "undefined") return "";
    const code = referral.data?.code;
    if (!code) return "";
    return `${window.location.origin}/r/${code}`;
  }, [referral.data?.code]);

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <h2 className="font-display text-lg font-semibold">Your progress</h2>
        {points.data ? (
          <p className="mt-3 text-sm text-[var(--muted)]">
            Level {points.data.level} · {points.data.balance} points (
            {points.data.lifetime} lifetime)
          </p>
        ) : (
          <p className="mt-3 text-sm text-[var(--muted)]">Loading points…</p>
        )}
        {points.data?.badges?.length ? (
          <ul className="mt-3 flex flex-wrap gap-2 text-xs">
            {points.data.badges.map((b) => (
              <li
                key={b.slug}
                className="rounded-full border border-[var(--border)] px-2 py-1"
              >
                {b.name}
              </li>
            ))}
          </ul>
        ) : null}
      </Card>
      <Card>
        <h2 className="font-display text-lg font-semibold">Refer friends</h2>
        {shareUrl ? (
          <p className="mt-3 break-all font-mono text-xs text-[var(--muted)]">
            {shareUrl}
          </p>
        ) : (
          <p className="mt-3 text-sm text-[var(--muted)]">Loading referral link…</p>
        )}
        <form
          className="mt-4 flex flex-wrap gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            claim.mutate();
          }}
        >
          <Input
            placeholder="Friend’s code"
            value={claimCode}
            onChange={(e) => setClaimCode(e.target.value)}
            className="max-w-[180px]"
          />
          <Button type="submit" size="sm" disabled={claim.isPending || !claimCode.trim()}>
            Claim
          </Button>
        </form>
        {msg ? (
          <p className="mt-2 text-xs text-[var(--muted)]" role="status">
            {msg}
          </p>
        ) : null}
      </Card>
    </div>
  );
}
