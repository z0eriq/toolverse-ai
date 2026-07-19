"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { NewsletterForm } from "@/components/NewsletterForm";
import { getSiteName } from "@/lib/utils";

export function Footer() {
  const t = useTranslations("footer");
  const year = new Date().getFullYear();
  const site = getSiteName();

  return (
    <footer className="mt-auto border-t border-[var(--border)] bg-[color-mix(in_oklab,var(--card)_70%,transparent)]">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4">
        <div className="sm:col-span-2 lg:col-span-1">
          <p className="font-display text-lg font-semibold tracking-tight">
            <span className="text-gradient">ToolVerse</span> AI
          </p>
          <p className="mt-2 max-w-md text-sm text-[var(--muted)]">
            Free online tools for developers, writers, and creators — privacy-first
            and built for real work.
          </p>
          <p className="mt-4 text-sm font-semibold">{t("newsletterTitle")}</p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {t("newsletterSupporting")}
          </p>
          <NewsletterForm />
        </div>
        <div>
          <p className="text-sm font-semibold">{t("product")}</p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--muted)]">
            <li>
              <Link href="/#tools" className="hover:text-[var(--foreground)]">
                Tools
              </Link>
            </li>
            <li>
              <Link href="/pricing" className="hover:text-[var(--foreground)]">
                Pricing
              </Link>
            </li>
            <li>
              <Link href="/blog" className="hover:text-[var(--foreground)]">
                Blog
              </Link>
            </li>
            <li>
              <Link href="/developers" className="hover:text-[var(--foreground)]">
                {t("developers")}
              </Link>
            </li>
            <li>
              <Link href="/enterprise" className="hover:text-[var(--foreground)]">
                Enterprise
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold">{t("company")}</p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--muted)]">
            <li>
              <Link href="/about" className="hover:text-[var(--foreground)]">
                About
              </Link>
            </li>
            <li>
              <Link href="/contact" className="hover:text-[var(--foreground)]">
                Contact
              </Link>
            </li>
            <li>
              <Link
                href="/editorial-policy"
                className="hover:text-[var(--foreground)]"
              >
                Editorial policy
              </Link>
            </li>
            <li>
              <Link href="/community" className="hover:text-[var(--foreground)]">
                Community
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold">{t("legal")}</p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--muted)]">
            <li>
              <Link href="/privacy" className="hover:text-[var(--foreground)]">
                {t("privacy")}
              </Link>
            </li>
            <li>
              <Link href="/terms" className="hover:text-[var(--foreground)]">
                {t("terms")}
              </Link>
            </li>
            <li>
              <a
                href="mailto:support@tool-verse.online"
                className="hover:text-[var(--foreground)]"
              >
                support@tool-verse.online
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-[var(--border)] py-4 text-center text-xs text-[var(--muted)]">
        © {year} {site}. {t("rights")}
      </div>
    </footer>
  );
}
