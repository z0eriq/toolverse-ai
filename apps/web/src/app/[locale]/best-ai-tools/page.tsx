import type { Metadata } from "next";
import {
  AuthorityProgrammaticPage,
  authorityGenerateMetadata,
} from "@/components/AuthorityProgrammaticPage";

export const revalidate = 3600;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  return authorityGenerateMetadata(locale, "best-ai-tools");
}

export default async function BestAiToolsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  return <AuthorityProgrammaticPage locale={locale} slug="best-ai-tools" />;
}
