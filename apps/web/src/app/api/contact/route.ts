import { NextResponse } from "next/server";
import { z } from "zod";

const bodySchema = z.object({
  name: z.string().trim().min(2).max(120),
  email: z.string().trim().email().max(254),
  message: z.string().trim().min(10).max(5000),
});

/**
 * Contact intake endpoint. Validates and acknowledges submissions.
 * Production mail delivery can be wired to EMAIL_* / provider later.
 */
export async function POST(request: Request) {
  let json: unknown;
  try {
    json = await request.json();
  } catch {
    return NextResponse.json(
      { success: false, error: "Invalid JSON body" },
      { status: 400 },
    );
  }

  const parsed = bodySchema.safeParse(json);
  if (!parsed.success) {
    return NextResponse.json(
      { success: false, error: "Please provide a valid name, email, and message." },
      { status: 400 },
    );
  }

  // Structured log for operators; do not echo PII beyond server logs.
  console.info("[contact]", {
    at: new Date().toISOString(),
    name: parsed.data.name.slice(0, 40),
    emailDomain: parsed.data.email.split("@")[1] ?? "",
    messageLength: parsed.data.message.length,
  });

  return NextResponse.json({
    success: true,
    data: {
      received: true,
      supportEmail: "support@tool-verse.online",
    },
  });
}
