import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import { Card } from "@/components/ui/card";
import { ApiKeysPanel } from "@/features/developers/api-keys-panel";
import { getApiUrl } from "@/lib/utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "developers" });
  return buildPageMetadata({
    title: t("title"),
    description: t("supporting"),
    path: "/developers",
    locale,
  });
}

export default async function DevelopersPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("developers");
  const apiBase = getApiUrl();

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <div className="max-w-2xl">
        <h1 className="font-display text-4xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="mt-3 text-[var(--muted)]">{t("supporting")}</p>
      </div>

      <div className="mt-12 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <h2 className="font-display text-xl font-semibold">{t("docsTitle")}</h2>
          <p className="mt-2 text-sm text-[var(--muted)]">{t("docsSupporting")}</p>

          <div className="mt-6 space-y-5 text-sm">
            <section>
              <h3 className="font-semibold">{t("authHeading")}</h3>
              <p className="mt-2 text-[var(--muted)]">{t("authBody")}</p>
              <pre className="mt-3 overflow-x-auto rounded-[var(--radius-md)] border border-[var(--border)] bg-[color-mix(in_oklab,var(--foreground)_4%,transparent)] p-3 font-mono text-xs">
{`curl -X GET "${apiBase}/tools/" \\
  -H "X-API-Key: tv_live_…" \\
  -H "Accept: application/json"`}
              </pre>
            </section>

            <section>
              <h3 className="font-semibold">{t("rateHeading")}</h3>
              <ul className="mt-2 list-disc space-y-1 ps-5 text-[var(--muted)]">
                <li>{t("rateDefault")}</li>
                <li>{t("rateQuota")}</li>
                <li>{t("rateHeaders")}</li>
              </ul>
            </section>

            <section>
              <h3 className="font-semibold">{t("endpointsHeading")}</h3>
              <ul className="mt-2 space-y-2 font-mono text-xs text-[var(--muted)]">
                <li>GET {apiBase}/tools/</li>
                <li>GET {apiBase}/tools/{"{slug}"}/</li>
                <li>POST {apiBase}/t/dynamic/{"{slug}"}/run/</li>
                <li>POST {apiBase}/jobs/</li>
                <li>GET {apiBase}/jobs/{"{id}"}/</li>
              </ul>
            </section>

            <section>
              <h3 className="font-semibold">{t("openapiHeading")}</h3>
              <p className="mt-2 text-[var(--muted)]">{t("openapiBody")}</p>
              <a
                href="/openapi.json"
                className="mt-3 inline-flex text-sm font-medium text-[var(--accent)] hover:underline"
              >
                {t("openapiLink")}
              </a>
            </section>

            <section>
              <h3 className="font-semibold">{t("sdkHeading")}</h3>
              <p className="mt-2 text-[var(--muted)]">{t("sdkBody")}</p>
              <pre className="mt-3 overflow-x-auto rounded-[var(--radius-md)] border border-[var(--border)] bg-[color-mix(in_oklab,var(--foreground)_4%,transparent)] p-3 font-mono text-xs">
{`npm install @toolverse/api-client

import { ToolVerseApiClient } from "@toolverse/api-client";

const client = new ToolVerseApiClient({
  apiKey: process.env.TOOLVERSE_API_KEY!,
  clientPlatform: "web",
});

const tools = await client.listTools({ compact: true });`}
              </pre>
            </section>

            <section>
              <h3 className="font-semibold">{t("billingHeading")}</h3>
              <p className="mt-2 text-[var(--muted)]">{t("billingBody")}</p>
              <ul className="mt-2 list-disc space-y-1 ps-5 text-[var(--muted)]">
                <li>{t("billingInvoices")}</li>
                <li>{t("billingAnalytics")}</li>
              </ul>
            </section>

            <section>
              <h3 className="font-semibold">{t("enterpriseHeading")}</h3>
              <p className="mt-2 text-[var(--muted)]">{t("enterpriseBody")}</p>
              <ul className="mt-2 list-disc space-y-1 ps-5 text-[var(--muted)]">
                <li>{t("enterpriseAnalytics")}</li>
                <li>{t("enterpriseOrgs")}</li>
              </ul>
              <a
                href={`/${locale}/enterprise`}
                className="mt-3 inline-flex text-sm font-medium text-[var(--accent)] hover:underline"
              >
                Enterprise sales →
              </a>
            </section>
          </div>
        </Card>

        <ApiKeysPanel />
      </div>
    </div>
  );
}
