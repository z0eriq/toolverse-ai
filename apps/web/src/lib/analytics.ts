"use client";

import { api } from "./api";

const UTM_STORAGE_KEY = "tv_utm";

function sessionId(): string {
  if (typeof window === "undefined") return "server";
  const key = "tv_sid";
  try {
    let id = sessionStorage.getItem(key);
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem(key, id);
    }
    return id;
  } catch {
    return "anonymous";
  }
}

/** Capture UTM params from the URL into sessionStorage once per session. */
export function captureUtmFromUrl(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const existing = sessionStorage.getItem(UTM_STORAGE_KEY);
    if (existing) {
      try {
        return JSON.parse(existing) as Record<string, string>;
      } catch {
        /* fall through and re-capture */
      }
    }
    const params = new URLSearchParams(window.location.search);
    const utm: Record<string, string> = {};
    for (const key of ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]) {
      const value = params.get(key);
      if (value) utm[key] = value.slice(0, 128);
    }
    const campaignKey = params.get("campaign_key") || params.get("utm_campaign") || "";
    if (campaignKey) utm.campaign_key = campaignKey.slice(0, 128);
    if (Object.keys(utm).length > 0) {
      sessionStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(utm));
    }
    return utm;
  } catch {
    return {};
  }
}

export function getStoredUtm(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const raw = sessionStorage.getItem(UTM_STORAGE_KEY);
    if (!raw) return captureUtmFromUrl();
    return JSON.parse(raw) as Record<string, string>;
  } catch {
    return {};
  }
}

function attributionPayload(): {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  campaign_key?: string;
  properties: Record<string, unknown>;
} {
  const utm = getStoredUtm();
  return {
    utm_source: utm.utm_source || undefined,
    utm_medium: utm.utm_medium || undefined,
    utm_campaign: utm.utm_campaign || undefined,
    campaign_key: utm.campaign_key || undefined,
    properties: { ...utm },
  };
}

export function trackPageView(path: string): void {
  captureUtmFromUrl();
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "page_view",
      session_id: sessionId(),
      path,
      ...attr,
      properties: {
        ...attr.properties,
        referrer: typeof document !== "undefined" ? document.referrer : "",
      },
    })
    .catch(() => undefined);
}

export function trackToolUse(toolId: string, action = "run"): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "tool_use",
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      tool_id: toolId,
      ...attr,
      properties: { ...attr.properties, tool_id: toolId, action },
    })
    .catch(() => undefined);
}

export function trackToolComplete(toolId: string): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "tool_complete",
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      tool_id: toolId,
      ...attr,
      properties: { ...attr.properties, tool_id: toolId, action: "complete" },
    })
    .catch(() => undefined);
}

export function trackPremiumIntent(source: string): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "premium_intent",
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      ...attr,
      properties: { ...attr.properties, source },
    })
    .catch(() => undefined);
}

/** Client stub for checkout / revenue intent events (premium_intent or checkout_start). */
export function trackRevenueEvent(
  name: "premium_intent" | "checkout_start" = "checkout_start",
  meta: Record<string, unknown> = {},
): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name,
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      ...attr,
      properties: { ...attr.properties, ...meta },
    })
    .catch(() => undefined);
}

export function toolImpression(toolId: string): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "tool_impression",
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      tool_id: toolId,
      ...attr,
      properties: { ...attr.properties, tool_id: toolId },
    })
    .catch(() => undefined);
}

export function toolClick(toolId: string): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "tool_click",
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      tool_id: toolId,
      ...attr,
      properties: { ...attr.properties, tool_id: toolId },
    })
    .catch(() => undefined);
}

export function trackSearch(query: string): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "search",
      session_id: sessionId(),
      path: typeof window !== "undefined" ? window.location.pathname : undefined,
      ...attr,
      properties: { ...attr.properties, q: query },
    })
    .catch(() => undefined);
}

export function trackShareClick(channel: string, path?: string): void {
  const attr = attributionPayload();
  void api
    .trackEvent({
      name: "share_click",
      session_id: sessionId(),
      path:
        path ??
        (typeof window !== "undefined" ? window.location.pathname : undefined),
      ...attr,
      properties: { ...attr.properties, channel },
    })
    .catch(() => undefined);
}
