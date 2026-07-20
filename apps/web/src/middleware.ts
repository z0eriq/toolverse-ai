import createIntlMiddleware from "next-intl/middleware";
import { type NextRequest, NextResponse } from "next/server";
import { routing } from "./i18n/routing";
import { updateSession } from "./utils/supabase/middleware";

const handleI18nRouting = createIntlMiddleware(routing);

const PROTECTED_SEGMENT =
  /\/(dashboard|favorites|history|workspace|workflows|creator|admin)(\/|$)/;

function localeFromPath(pathname: string): string {
  const first = pathname.split("/")[1];
  if (first && (routing.locales as readonly string[]).includes(first)) {
    return first;
  }
  return routing.defaultLocale;
}

function copyCookies(from: NextResponse, to: NextResponse) {
  from.cookies.getAll().forEach((cookie) => {
    to.cookies.set(cookie);
  });
  return to;
}

export default async function middleware(request: NextRequest) {
  const { response: supabaseResponse, user } = await updateSession(request);
  const { pathname } = request.nextUrl;

  // Skip i18n for the OAuth/email PKCE callback.
  if (pathname.startsWith("/auth/callback")) {
    return supabaseResponse;
  }

  if (PROTECTED_SEGMENT.test(pathname) && !user) {
    const locale = localeFromPath(pathname);
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = `/${locale}/auth/login`;
    loginUrl.searchParams.set("next", pathname);
    return copyCookies(supabaseResponse, NextResponse.redirect(loginUrl));
  }

  const response = handleI18nRouting(request);
  return copyCookies(supabaseResponse, response);
}

export const config = {
  matcher: [
    "/",
    "/(ar|en|es|fr|de|pt|zh)/:path*",
    "/((?!api|_next|_vercel|.*\\..*).*)",
  ],
};
