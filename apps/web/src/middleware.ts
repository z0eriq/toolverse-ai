import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
  matcher: [
    "/",
    "/(ar|en|es|fr|de|pt|zh)/:path*",
    "/((?!api|_next|_vercel|.*\\..*).*)",
  ],
};
