import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { api, type PlanItem } from "@/lib/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pricing" });
  return buildPageMetadata({
    title: t("title"),
    description: t("supporting"),
    path: "/pricing",
    locale,
  });
}

async function loadPlans(): Promise<PlanItem[]> {
  try {
    return await api.plans();
  } catch {
    return [
      {
        slug: "free",
        name: "Free",
        description: "Core tools with community support.",
        price_cents: 0,
        currency: "USD",
        features: ["All free tools", "Local history", "Ad-supported"],
      },
      {
        slug: "premium",
        name: "Pro",
        description: "Unlimited runs, no ads, higher API quotas.",
        price_cents: 900,
        currency: "USD",
        features: ["Unlimited tool runs", "Ads free", "Synced history", "Priority support"],
        monthly_tool_runs: -1,
        ads_free: true,
      },
    ];
  }
}

export default async function PricingPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("pricing");
  const plans = await loadPlans();

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="font-display text-4xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="mt-3 text-[var(--muted)]">{t("supporting")}</p>
      </div>
      <div className="mt-12 grid gap-6 md:grid-cols-2">
        {plans.map((plan) => {
          const features = Array.isArray(plan.features)
            ? plan.features
            : Object.keys(plan.features ?? {});
          const price = (plan.price_cents / 100).toFixed(plan.price_cents % 100 === 0 ? 0 : 2);
          return (
            <Card key={plan.slug} className="flex flex-col">
              <p className="text-sm uppercase tracking-wider text-[var(--accent)]">
                {plan.slug === "premium" ? t("premium") : t("free")}
              </p>
              <h2 className="mt-2 font-display text-2xl font-semibold">{plan.name}</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">{plan.description}</p>
              <p className="mt-6 font-display text-4xl font-semibold">
                ${price}
                <span className="text-base font-normal text-[var(--muted)]">
                  {plan.price_cents > 0 ? t("perMonth") : ""}
                </span>
              </p>
              <ul className="mt-6 space-y-2 text-sm text-[var(--muted)]">
                {features.map((f) => (
                  <li key={f}>• {f}</li>
                ))}
              </ul>
              <div className="mt-8">
                <Button asChild className="w-full">
                  <Link href="/auth/register">{t("cta")}</Link>
                </Button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
