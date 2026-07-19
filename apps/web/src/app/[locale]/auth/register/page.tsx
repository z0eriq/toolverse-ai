import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import { Card } from "@/components/ui/card";
import { RegisterForm } from "@/features/auth/register-form";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "auth" });
  return buildPageMetadata({
    title: t("registerTitle"),
    description: t("registerSupporting"),
    path: "/auth/register",
    locale,
    noIndex: true,
  });
}

export default async function RegisterPage({
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
        <h1 className="font-display text-2xl font-semibold tracking-tight">
          {t("registerTitle")}
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">{t("registerSupporting")}</p>
        <div className="mt-6">
          <RegisterForm />
        </div>
      </Card>
    </div>
  );
}
