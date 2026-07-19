import { ImageResponse } from "next/og";
import { getSiteName } from "@/lib/utils";

export const runtime = "edge";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get("title") ?? getSiteName();
  const subtitle =
    searchParams.get("subtitle") ?? "Free premium online tools for everyone";

  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#07090c",
          padding: "64px",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "radial-gradient(ellipse 70% 50% at 20% 10%, rgba(20,184,166,0.35), transparent), radial-gradient(ellipse 50% 40% at 90% 20%, rgba(34,211,238,0.22), transparent)",
          }}
        />
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 18,
              height: 18,
              borderRadius: 4,
              background: "linear-gradient(135deg, #14b8a6, #22d3ee)",
            }}
          />
          <div style={{ color: "#e8eef6", fontSize: 28, fontWeight: 600 }}>
            {getSiteName()}
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 980 }}>
          <div
            style={{
              color: "#e8eef6",
              fontSize: 64,
              fontWeight: 700,
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
            }}
          >
            {title}
          </div>
          <div style={{ color: "#8b9bb0", fontSize: 28, lineHeight: 1.35 }}>
            {subtitle.slice(0, 140)}
          </div>
        </div>
        <div style={{ color: "#14b8a6", fontSize: 22, fontWeight: 600 }}>
          toolverse.ai
        </div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
