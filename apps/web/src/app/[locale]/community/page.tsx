import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { CommunityPageClient } from "./community-client";
import { buildPageMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  return buildPageMetadata({
    title: "Community",
    description: "Public collections and creators on ToolVerse AI.",
    path: "/community",
    locale,
  });
}

export default async function CommunityPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  return <CommunityPageClient />;
}
