import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "ToolVerse AI",
    short_name: "ToolVerse",
    description:
      "Every tool you need — format, convert, encode, and analyze in one premium workspace.",
    start_url: "/",
    display: "standalone",
    background_color: "#0a0a0a",
    theme_color: "#14b8a6",
    orientation: "portrait-primary",
    categories: ["productivity", "utilities", "developer"],
    icons: [
      {
        src: "/favicon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any",
      },
      {
        src: "/favicon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "maskable",
      },
    ],
  };
}
