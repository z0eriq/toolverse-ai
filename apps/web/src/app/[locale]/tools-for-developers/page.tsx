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
  return authorityGenerateMetadata(locale, "tools-for-developers");
}

export default async function ToolsForDevelopersPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  return (
    <AuthorityProgrammaticPage locale={locale} slug="tools-for-developers" />
  );
}
