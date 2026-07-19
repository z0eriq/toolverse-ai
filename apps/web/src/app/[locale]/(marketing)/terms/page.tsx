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
    title: "Terms of Service — ToolVerse AI",
    description:
      "Terms of Service for ToolVerse AI at tool-verse.online: acceptable use, warranties, liability limits, intellectual property, and contact information.",
    path: "/terms",
    locale,
  });
}

export default async function TermsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">
        Terms of Service
      </h1>
      <p className="mt-4 text-lg text-[var(--muted)]">
        Effective date: July 19, 2026. By accessing or using ToolVerse AI at
        tool-verse.online (“Service”), you agree to these Terms of Service
        (“Terms”). If you do not agree, do not use the Service.
      </p>

      <div className="mt-10 space-y-10 text-base leading-relaxed">
        <section>
          <h2 className="font-display text-2xl font-semibold">1. The Service</h2>
          <p className="mt-3 text-[var(--muted)]">
            ToolVerse provides online tools, documentation, and related features
            for developers and creators. Some features are free; others may
            require an account or paid plan. We may change, suspend, or
            discontinue features with or without notice, subject to applicable
            law and any contractual commitments for paid plans.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">2. Accounts</h2>
          <p className="mt-3 text-[var(--muted)]">
            You are responsible for accurate registration details and for keeping
            your credentials confidential. You must be old enough to form a
            binding contract in your jurisdiction. Notify us promptly of
            unauthorized account use at support@tool-verse.online.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">3. Acceptable use</h2>
          <p className="mt-3 text-[var(--muted)]">You agree not to:</p>
          <ul className="mt-3 list-disc space-y-2 ps-5 text-[var(--muted)]">
            <li>
              Use the Service for unlawful activity, fraud, harassment, or
              infringement of others’ rights
            </li>
            <li>
              Attempt to disrupt, overload, reverse engineer (except where
              permitted by law), or bypass security or rate limits
            </li>
            <li>
              Upload malware, scrape the Service in an abusive way, or use
              automated means that degrade availability for others
            </li>
            <li>
              Misrepresent affiliation with ToolVerse or use our marks without
              permission
            </li>
            <li>
              Process data you are not authorized to handle, including personal
              data of others without a lawful basis
            </li>
          </ul>
          <p className="mt-3 text-[var(--muted)]">
            We may suspend or terminate access for violations or to protect the
            Service and its users.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">4. Your content</h2>
          <p className="mt-3 text-[var(--muted)]">
            You retain ownership of content you submit. You grant ToolVerse a
            limited license to process that content solely to provide the
            features you request (for example running a tool or syncing history).
            You represent that you have the rights needed to submit the content.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">5. Intellectual property</h2>
          <p className="mt-3 text-[var(--muted)]">
            The Service—including software, design, logos, documentation, and
            editorial content—is owned by ToolVerse or its licensors and is
            protected by intellectual property laws. Except for the limited right
            to use the Service as offered, no license is granted. Feedback you
            provide may be used by us without obligation to you.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">6. Third-party services and ads</h2>
          <p className="mt-3 text-[var(--muted)]">
            The Service may integrate third-party providers (hosting, payments,
            analytics, advertising). Their terms and privacy practices apply to
            their processing. Free plans may include advertising. See our{" "}
            <Link href="/privacy" className="text-[var(--accent)] hover:underline">
              Privacy Policy
            </Link>{" "}
            for details.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">7. Service availability</h2>
          <p className="mt-3 text-[var(--muted)]">
            We aim for high availability but do not guarantee uninterrupted or
            error-free operation. Maintenance, outages, dependency failures, and
            force majeure events may affect access. Paid plan service levels, if
            any, are described in the applicable plan materials.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">8. No warranty</h2>
          <p className="mt-3 text-[var(--muted)]">
            THE SERVICE IS PROVIDED “AS IS” AND “AS AVAILABLE.” TO THE MAXIMUM
            EXTENT PERMITTED BY LAW, TOOLVERSE DISCLAIMS ALL WARRANTIES, EXPRESS
            OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS FOR A PARTICULAR
            PURPOSE, AND NON-INFRINGEMENT. Tool outputs may contain errors; you
            are responsible for verifying results before relying on them in
            production systems.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">9. Limitation of liability</h2>
          <p className="mt-3 text-[var(--muted)]">
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, TOOLVERSE AND ITS TEAM SHALL
            NOT BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR
            PUNITIVE DAMAGES, OR FOR LOST PROFITS, DATA, OR GOODWILL, ARISING
            FROM YOUR USE OF THE SERVICE. OUR TOTAL LIABILITY FOR ANY CLAIM
            RELATING TO THE SERVICE SHALL NOT EXCEED THE GREATER OF (A) THE
            AMOUNTS YOU PAID US IN THE TWELVE MONTHS BEFORE THE CLAIM OR (B) ONE
            HUNDRED U.S. DOLLARS (USD $100). Some jurisdictions do not allow
            certain limitations; in those cases, our liability is limited to the
            fullest extent allowed.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">10. Indemnity</h2>
          <p className="mt-3 text-[var(--muted)]">
            You agree to indemnify and hold harmless ToolVerse from claims
            arising out of your misuse of the Service, your content, or your
            violation of these Terms or applicable law.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">11. Changes to Terms</h2>
          <p className="mt-3 text-[var(--muted)]">
            We may update these Terms. Material changes will be reflected by an
            updated effective date. Continued use after changes constitutes
            acceptance where permitted by law.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">12. Contact</h2>
          <p className="mt-3 text-[var(--muted)]">
            Questions about these Terms:{" "}
            <a
              href="mailto:support@tool-verse.online"
              className="text-[var(--accent)] hover:underline"
            >
              support@tool-verse.online
            </a>{" "}
            or our{" "}
            <Link href="/contact" className="text-[var(--accent)] hover:underline">
              contact page
            </Link>
            .
          </p>
        </section>
      </div>
    </div>
  );
}
