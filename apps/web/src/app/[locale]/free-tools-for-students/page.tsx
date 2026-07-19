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
  return authorityGenerateMetadata(locale, "free-tools-for-students");
}

export default async function FreeToolsForStudentsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  return (
    <AuthorityProgrammaticPage locale={locale} slug="free-tools-for-students" />
  );
}
