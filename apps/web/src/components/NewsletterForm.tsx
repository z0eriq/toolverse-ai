"use client";

import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ApiError, api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function NewsletterForm() {
  const t = useTranslations("footer");
  const locale = useLocale();
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "error">(
    "idle",
  );
  const [message, setMessage] = useState<string | null>(null);

  return (
    <form
      className="mt-4 space-y-3"
      onSubmit={async (e) => {
        e.preventDefault();
        setStatus("loading");
        setMessage(null);
        try {
          await api.newsletter.subscribe(email.trim(), locale);
          setStatus("ok");
          setMessage(t("newsletterSuccess"));
          setEmail("");
        } catch (err) {
          setStatus("error");
          setMessage(
            err instanceof ApiError ? err.message : t("newsletterError"),
          );
        }
      }}
    >
      <Label htmlFor="newsletter-email" className="sr-only">
        {t("newsletterEmail")}
      </Label>
      <div className="flex flex-col gap-2 sm:flex-row">
        <Input
          id="newsletter-email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t("newsletterPlaceholder")}
          className="flex-1"
        />
        <Button type="submit" disabled={status === "loading"}>
          {status === "loading" ? t("newsletterSubmitting") : t("newsletterCta")}
        </Button>
      </div>
      {message ? (
        <p
          className={
            status === "error"
              ? "text-xs text-[var(--color-danger)]"
              : "text-xs text-[var(--muted)]"
          }
          role={status === "error" ? "alert" : "status"}
        >
          {message}
        </p>
      ) : null}
    </form>
  );
}
