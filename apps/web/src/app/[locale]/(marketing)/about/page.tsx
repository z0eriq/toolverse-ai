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
    title: "About ToolVerse AI — Free Online Tools for Developers & Creators",
    description:
      "Learn about ToolVerse AI at tool-verse.online: our mission to ship fast, privacy-first online tools for developers and creators, and how we operate with transparency.",
    path: "/about",
    locale,
  });
}

export default async function AboutPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">
        About ToolVerse AI
      </h1>
      <p className="mt-4 text-lg text-[var(--muted)]">
        ToolVerse AI is a free online toolbox at{" "}
        <a
          href="https://tool-verse.online"
          className="text-[var(--accent)] hover:underline"
        >
          tool-verse.online
        </a>
        , built for developers, designers, writers, and creators who need reliable
        utilities without installing software or uploading sensitive files to
        unknown servers.
      </p>

      <div className="mt-10 space-y-10 text-base leading-relaxed">
        <section>
          <h2 className="font-display text-2xl font-semibold">Our mission</h2>
          <p className="mt-3 text-[var(--muted)]">
            We believe everyday technical tasks should be fast, clear, and
            accessible. Whether you are formatting JSON, converting colors,
            compressing an image, or checking a JWT, ToolVerse aims to give you
            a trustworthy workspace that loads quickly, works on any modern
            browser, and stays out of your way.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            Our goal is not to replace professional software, but to cover the
            high-frequency jobs that interrupt deep work: small conversions,
            previews, encodings, and checks you should be able to finish in
            seconds.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Privacy-first by design</h2>
          <p className="mt-3 text-[var(--muted)]">
            Whenever practical, tools run in your browser. Client-side processing
            means your payloads, tokens, and documents do not need to leave your
            device for many common workflows. When a feature requires a server
            (for example heavier processing or account sync), we document what is
            sent and why.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            We do not sell personal data. Advertising partners, if present, are
            disclosed in our Privacy Policy so you can make an informed choice
            about cookies and third-party scripts.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Quality commitment</h2>
          <p className="mt-3 text-[var(--muted)]">
            Every tool and guide is maintained with production standards in mind:
            accurate results, accessible interfaces, clear error messages, and
            documentation that reflects how the tool actually behaves. We prefer
            fewer polished utilities over a long list of unfinished experiments.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            Editorial content—blog articles, tool guides, and policy pages—is
            written and reviewed by the ToolVerse team so readers get practical
            advice rather than keyword filler. Corrections are welcomed and
            published when we find material errors.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Who operates ToolVerse</h2>
          <p className="mt-3 text-[var(--muted)]">
            ToolVerse AI is operated by the ToolVerse team. We build and host the
            platform, maintain the tool catalog, and publish help content under
            the ToolVerse Editorial Team byline. For partnership, press, or
            support inquiries, reach us through the contact page or email
            support@tool-verse.online.
          </p>
          <p className="mt-3 text-[var(--muted)]">
            We are committed to transparent ownership of this property, clear
            contact channels, and policies that meet the expectations of users
            and advertising partners who require identifiable publishers with
            substantive, original content.
          </p>
        </section>

        <section>
          <h2 className="font-display text-2xl font-semibold">Get in touch</h2>
          <p className="mt-3 text-[var(--muted)]">
            Questions about a tool, a bug report, or feedback on our policies?{" "}
            <Link href="/contact" className="text-[var(--accent)] hover:underline">
              Contact us
            </Link>{" "}
            — we read every message.
          </p>
        </section>

        <p className="text-sm text-[var(--muted)]">Last updated: July 2026</p>
      </div>
    </div>
  );
}
