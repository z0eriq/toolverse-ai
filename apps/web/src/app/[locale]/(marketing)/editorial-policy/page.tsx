import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { buildPageMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  return buildPageMetadata({
    title: "Editorial Policy — ToolVerse AI E-E-A-T Standards",
    description:
      "How the ToolVerse Editorial Team creates, reviews, updates, and corrects guides and articles—including advertising disclosure and authorship standards.",
    path: "/editorial-policy",
    locale,
  });
}

export default async function EditorialPolicyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">
        Editorial Policy
      </h1>
      <p className="mt-4 text-lg text-[var(--muted)]">
        ToolVerse AI publishes guides, blog articles, and tool documentation to
        help people use online utilities safely and effectively. This policy
        describes how we uphold experience, expertise, authoritativeness, and
        trustworthiness (E-E-A-T) in our content.
      </p>

      <div className="mt-10 space-y-10 text-base leading-relaxed">
        <section>
          <h2 className="font-display text-2xl font-semibold">Authorship</h2>
          <p className="mt-3 text-[var(--muted)]">
            Editorial content is produced by the{" "}
            <strong className="text-[var(--foreground)]">
              ToolVerse Editorial Team
            </strong>
            —operators and contributors who build and maintain the product.
            Bylines on articles and guides reflect that collective ownership
            unless a named specialist author is credited. We do not publish
            anonymous product claims without an accountable publisher identity.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Accuracy standards</h2>
          <p className="mt-3 text-[var(--muted)]">
            Technical steps are verified against the live ToolVerse tools or
            widely accepted industry behavior (for example how JWT segments are
            structured, or how image compression trade-offs work). We prefer
            concrete procedures over vague marketing language. Where a topic is
            contested or depends on browser support, we state assumptions clearly.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Review process</h2>
          <p className="mt-3 text-[var(--muted)]">
            Before publication, drafts are checked for factual correctness,
            clarity, broken links, and alignment with actual product behavior.
            Significant how-to guides are re-tested after material UI or
            algorithm changes. Legal pages (Privacy, Terms) are reviewed when
            product practices or partner integrations change.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Updates</h2>
          <p className="mt-3 text-[var(--muted)]">
            Articles and tool guides include or reference update dates when
            practical. We refresh evergreen topics (compression, PDF workflows,
            productivity tooling) on a periodic schedule and sooner when
            standards or our product surface change in ways that would mislead
            readers.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Corrections</h2>
          <p className="mt-3 text-[var(--muted)]">
            If you find an error, email{" "}
            <a
              href="mailto:support@tool-verse.online"
              className="text-[var(--accent)] hover:underline"
            >
              support@tool-verse.online
            </a>{" "}
            or use the{" "}
            <Link href="/contact" className="text-[var(--accent)] hover:underline">
              contact form
            </Link>
            . Material factual corrections are applied promptly; we may note
            significant corrections on the page when transparency helps readers.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Advertising disclosure</h2>
          <p className="mt-3 text-[var(--muted)]">
            Free access to ToolVerse may be supported by third-party advertising,
            including networks such as Google AdSense. Ads are labeled by the
            advertising provider. Editorial recommendations are not sold as
            sponsored placements unless clearly disclosed as advertising or
            sponsored content. Product mentions of ToolVerse tools reflect
            features we operate; they are not paid endorsements from unrelated
            third parties.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            Advertising partners do not write or approve our editorial copy.
            Privacy details about cookies and ad personalization appear in our{" "}
            <Link href="/privacy" className="text-[var(--accent)] hover:underline">
              Privacy Policy
            </Link>
            .
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Independence and conflicts</h2>
          <p className="mt-3 text-[var(--muted)]">
            When we compare categories of tools, we disclose that ToolVerse is
            one option among many. We aim for practical criteria (privacy model,
            speed, accuracy, cost) rather than ranking schemes designed only to
            promote ourselves. Affiliate relationships, if introduced later,
            will be disclosed on the relevant pages.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">User safety</h2>
          <p className="mt-3 text-[var(--muted)]">
            Guides that involve tokens, hashes, or personal documents emphasize
            safe handling: prefer client-side processing, avoid pasting
            production secrets into untrusted sites, and verify outputs before
            shipping to production. We never instruct readers to violate laws or
            platform terms.
          </p>
        </section>

        <p className="text-sm text-[var(--muted)]">Last updated: July 2026</p>
      </div>
    </div>
  );
}
