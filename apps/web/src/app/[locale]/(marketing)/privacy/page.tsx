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
    title: "Privacy Policy — ToolVerse AI",
    description:
      "How ToolVerse AI collects, uses, and protects information on tool-verse.online, including cookies, analytics, and advertising partners such as Google AdSense.",
    path: "/privacy",
    locale,
  });
}

export default async function PrivacyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">
        Privacy Policy
      </h1>
      <p className="mt-4 text-lg text-[var(--muted)]">
        Effective date: July 19, 2026. This Privacy Policy explains how ToolVerse
        AI (“ToolVerse,” “we,” “us”) handles information when you use
        tool-verse.online and related services.
      </p>

      <div className="mt-10 space-y-10 text-base leading-relaxed">
        <section>
          <h2 className="font-display text-2xl font-semibold">1. Who we are</h2>
          <p className="mt-3 text-[var(--muted)]">
            ToolVerse AI provides free and premium online tools for developers
            and creators. The service is operated by the ToolVerse team. For
            privacy questions, contact{" "}
            <a
              href="mailto:support@tool-verse.online"
              className="text-[var(--accent)] hover:underline"
            >
              support@tool-verse.online
            </a>
            .
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">2. Information we collect</h2>
          <p className="mt-3 text-[var(--muted)]">
            We collect information in three broad categories:
          </p>
          <ul className="mt-3 list-disc space-y-2 ps-5 text-[var(--muted)]">
            <li>
              <strong className="text-[var(--foreground)]">Account data</strong>{" "}
              — If you create an account, we store your email address, display
              name, authentication credentials (hashed), and plan or billing
              metadata needed to provide the service.
            </li>
            <li>
              <strong className="text-[var(--foreground)]">Usage data</strong>{" "}
              — We may log pages visited, tools opened, approximate device and
              browser type, referring URLs, timestamps, and similar technical
              diagnostics to keep the site reliable and improve features.
            </li>
            <li>
              <strong className="text-[var(--foreground)]">
                Communications
              </strong>{" "}
              — Messages you send via the contact form or email, including any
              details you choose to include.
            </li>
          </ul>
          <p className="mt-3 text-[var(--muted)]">
            Many tools process content locally in your browser. Content you paste
            into client-side tools is generally not uploaded to our servers unless
            a feature explicitly requires network processing (for example certain
            heavy conversions, API runs, or synced history). Do not paste secrets
            into tools unless you understand where processing occurs.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">3. How we use information</h2>
          <ul className="mt-3 list-disc space-y-2 ps-5 text-[var(--muted)]">
            <li>Operate, secure, and improve ToolVerse AI</li>
            <li>Provide accounts, support, and billing where applicable</li>
            <li>Measure performance and diagnose errors</li>
            <li>Comply with legal obligations and enforce our Terms</li>
            <li>
              Show relevant advertising when ads are enabled on free experiences
            </li>
          </ul>
          <p className="mt-3 text-[var(--muted)]">
            We do not sell your personal information. We do not use tool payload
            contents for advertising personalization.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">4. Cookies and similar technologies</h2>
          <p className="mt-3 text-[var(--muted)]">
            We use cookies and local storage for essential functions (session,
            preferences, security) and, where enabled, for analytics and
            advertising. You can control cookies through your browser settings.
            Blocking certain cookies may limit account or preference features.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">5. Analytics</h2>
          <p className="mt-3 text-[var(--muted)]">
            We may use first-party or third-party analytics to understand traffic
            patterns (for example which tools are popular and where errors
            occur). Analytics providers process technical identifiers such as IP
            address (often truncated), device information, and page paths
            according to their own privacy policies.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">
            6. Advertising and third parties (including Google AdSense)
          </h2>
          <p className="mt-3 text-[var(--muted)]">
            ToolVerse may display third-party advertisements, including ads
            served by Google AdSense or similar networks, to support free access
            to tools. These partners may use cookies, web beacons, and similar
            technologies to collect information about your visits to this and
            other websites in order to provide ads about goods and services of
            interest to you.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            Google’s use of advertising cookies enables it and its partners to
            serve ads based on your prior visits to ToolVerse and/or other sites
            on the Internet. You can opt out of personalized advertising by
            visiting{" "}
            <a
              href="https://www.google.com/settings/ads"
              className="text-[var(--accent)] hover:underline"
              rel="noopener noreferrer"
              target="_blank"
            >
              Google Ads Settings
            </a>
            , or visit{" "}
            <a
              href="https://www.aboutads.info/choices/"
              className="text-[var(--accent)] hover:underline"
              rel="noopener noreferrer"
              target="_blank"
            >
              aboutads.info
            </a>{" "}
            for broader industry opt-outs where available.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            Third-party vendors, including Google, use cookies to serve ads based
            on a user’s prior visits. We do not control all cookies set by ad
            partners. Please review their policies for details on data practices.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">7. Data sharing</h2>
          <p className="mt-3 text-[var(--muted)]">
            We share information only with service providers who help us run the
            site (hosting, email delivery, payment processors, analytics,
            advertising networks), when required by law, or to protect the rights
            and safety of users and ToolVerse. Providers are instructed to process
            data only for contracted purposes.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">8. Retention</h2>
          <p className="mt-3 text-[var(--muted)]">
            We retain account and support records for as long as your account is
            active or as needed to provide services, resolve disputes, and meet
            legal requirements. Logs and analytics are kept for shorter
            operational windows unless a longer period is required for security
            investigations.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">9. Your rights</h2>
          <p className="mt-3 text-[var(--muted)]">
            Depending on your location, you may have rights to access, correct,
            delete, or export personal data we hold about you, or to object to
            certain processing. To exercise these rights, email{" "}
            <a
              href="mailto:support@tool-verse.online"
              className="text-[var(--accent)] hover:underline"
            >
              support@tool-verse.online
            </a>
            . We may need to verify your identity before fulfilling a request.
            You may also delete your account where that feature is available in
            product settings.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">10. Children</h2>
          <p className="mt-3 text-[var(--muted)]">
            ToolVerse is not directed at children under 13 (or the equivalent
            minimum age in your jurisdiction). We do not knowingly collect
            personal information from children. If you believe a child has
            provided us data, contact us and we will take appropriate steps to
            delete it.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">11. International transfers</h2>
          <p className="mt-3 text-[var(--muted)]">
            We may process information in countries other than your own. Where
            required, we use appropriate safeguards for cross-border transfers.
            By using the service, you understand that your information may be
            transferred to and processed in these locations.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">12. Security</h2>
          <p className="mt-3 text-[var(--muted)]">
            We implement reasonable technical and organizational measures to
            protect information. No method of transmission or storage is
            completely secure; please use strong passwords and avoid submitting
            highly sensitive secrets through web forms unless necessary.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">13. Changes</h2>
          <p className="mt-3 text-[var(--muted)]">
            We may update this Policy from time to time. The effective date at
            the top will change when we do. Continued use of ToolVerse after an
            update constitutes acceptance of the revised Policy where permitted
            by law.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">14. Contact</h2>
          <p className="mt-3 text-[var(--muted)]">
            Privacy requests and questions:{" "}
            <a
              href="mailto:support@tool-verse.online"
              className="text-[var(--accent)] hover:underline"
            >
              support@tool-verse.online
            </a>
            . You can also use our{" "}
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
