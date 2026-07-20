import createIntlMiddleware from "next-intl/middleware";
import { NextRequest, NextResponse } from "next/server";
import { routing } from "./i18n/routing";
import { LOCALE_CHOSEN_COOKIE } from "./i18n/locale-preference";
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

/**
 * next-intl prefers NEXT_LOCALE over Accept-Language. For visitors who never
 * explicitly chose a language, strip that cookie so the browser/device language
 * wins (e.g. Arabic phones → /ar).
 */
function requestForLocaleNegotiation(request: NextRequest): NextRequest {
  const explicit = request.cookies.get(LOCALE_CHOSEN_COOKIE)?.value === "1";
  if (explicit || !request.cookies.get("NEXT_LOCALE")) {
    return request;
  }

  const kept = request.cookies
    .getAll()
    .filter((c) => c.name !== "NEXT_LOCALE")
    .map((c) => `${c.name}=${encodeURIComponent(c.value)}`)
    .join("; ");

  const headers = new Headers(request.headers);
  if (kept) headers.set("cookie", kept);
  else headers.delete("cookie");

  return new NextRequest(request.url, {
    headers,
    method: request.method,
  });
}

export default async function middleware(request: NextRequest) {
  const { response: supabaseResponse, user } = await updateSession(request);
  const { pathname } = request.nextUrl;

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

  const intlRequest = requestForLocaleNegotiation(request);
  const response = handleI18nRouting(intlRequest);
  return copyCookies(supabaseResponse, response);
}

export const config = {
  matcher: [
    "/",
    "/(ar|en|es|fr|de|pt|zh)/:path*",
    "/((?!api|_next|_vercel|.*\\..*).*)",
  ],
};
