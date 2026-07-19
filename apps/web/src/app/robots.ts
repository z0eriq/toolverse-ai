import type { MetadataRoute } from "next";
import { getAppUrl } from "@/lib/utils";

export default function robots(): MetadataRoute.Robots {
  const base = getAppUrl();
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin", "/dashboard", "/favorites", "/history", "/workspace", "/api/"],
      },
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base,
  };
}
