import type { ReactNode } from "react";

/**
 * Root layout required by Next.js. Locale-specific <html>/<body>
 * live in app/[locale]/layout.tsx (next-intl pattern).
 */
export default function RootLayout({ children }: { children: ReactNode }) {
  return children;
}
