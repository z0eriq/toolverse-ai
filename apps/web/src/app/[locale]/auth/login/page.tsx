import type { Metadata } from "next";
import { Suspense } from "react";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import { Card } from "@/components/ui/card";
import { LoginForm } from "@/features/auth/login-form";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "auth" });
  return buildPageMetadata({
    title: t("loginTitle"),
    description: t("loginSupporting"),
    path: "/auth/login",
    locale,
    noIndex: true,
  });
}

export default async function LoginPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("auth");

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16">
      <Card>
        <h1 className="font-display text-2xl font-semibold tracking-tight">{t("loginTitle")}</h1>
        <p className="mt-2 text-sm text-[var(--muted)]">{t("loginSupporting")}</p>
        <div className="mt-6">
          <Suspense fallback={<p className="text-sm text-[var(--muted)]">…</p>}>
            <LoginForm />
          </Suspense>
        </div>
      </Card>
    </div>
  );
}
