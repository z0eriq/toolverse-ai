import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { ContactForm } from "@/components/ContactForm";
import { buildPageMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  return buildPageMetadata({
    title: "Contact ToolVerse AI — Support & Feedback",
    description:
      "Contact the ToolVerse AI team at support@tool-verse.online for product questions, bug reports, privacy requests, and partnership inquiries.",
    path: "/contact",
    locale,
  });
}

export default async function ContactPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">
        Contact us
      </h1>
      <p className="mt-4 text-lg text-[var(--muted)]">
        Need help with a tool, found a bug, or have a privacy or partnership
        question? Send a message below or email us directly. We read every
        inquiry and typically respond within a few business days.
      </p>

      <div className="mt-8 rounded-[var(--radius-md)] border border-[var(--border)] p-5">
        <p className="text-sm text-[var(--muted)]">Email support</p>
        <a
          href="mailto:support@tool-verse.online"
          className="mt-1 inline-flex text-lg font-medium text-[var(--accent)] hover:underline"
        >
          support@tool-verse.online
        </a>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-2xl font-semibold">Send a message</h2>
        <p className="mt-2 text-sm text-[var(--muted)]">
          Include enough detail for us to reproduce an issue (tool name, browser,
          and what you expected versus what happened).
        </p>
        <div className="mt-6">
          <ContactForm />
        </div>
      </div>
    </div>
  );
}
