/**
 * ToolVerse AI API Client
 * Thin client for marketplace + mobile public endpoints.
 * Regenerated baseline via `manage.py generate_sdk`; extended for Market Domination.
 */

export type ApiClientOptions = {
  baseUrl?: string;
  apiKey: string;
  /** Sent as X-Client-Platform (ios | android | web | …). */
  clientPlatform?: string;
};

export type MobileTool = {
  slug: string;
  category: string;
  name: Record<string, string> | string;
  tool_id?: string;
  icon?: string;
};

export type MarketplaceOrg = {
  id: number;
  name: string;
  plan_tier?: string;
  [key: string]: unknown;
};

export type MarketplaceUsage = {
  [key: string]: unknown;
};

type ApiEnvelope<T> = {
  success?: boolean;
  data?: T;
};

export class ToolVerseApiClient {
  readonly baseUrl: string;
  readonly apiKey: string;
  readonly clientPlatform: string;

  constructor(options: ApiClientOptions) {
    this.baseUrl = (options.baseUrl || "https://api.toolverse.ai/api/v1").replace(
      /\/$/,
      "",
    );
    this.apiKey = options.apiKey;
    this.clientPlatform = options.clientPlatform || "sdk";
  }

  async request<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers || {});
    headers.set("Authorization", `Bearer ${this.apiKey}`);
    headers.set("Accept", "application/json");
    headers.set("X-Client-Platform", this.clientPlatform);
    if (init.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    const res = await fetch(
      `${this.baseUrl}${path.startsWith("/") ? path : `/${path}`}`,
      { ...init, headers },
    );
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`ToolVerse API ${res.status}: ${text}`);
    }
    const json = (await res.json()) as T | ApiEnvelope<T>;
    if (
      json &&
      typeof json === "object" &&
      "success" in json &&
      "data" in json
    ) {
      return (json as ApiEnvelope<T>).data as T;
    }
    return json as T;
  }

  /** Mobile-optimized tool catalog (`GET /mobile/tools/`). */
  listTools(params?: { compact?: boolean }) {
    const q = params?.compact ? "?compact=1" : "";
    return this.request<MobileTool[]>(`/mobile/tools/${q}`);
  }

  /** Developer org list (`GET /marketplace/orgs/`). */
  listOrgs() {
    return this.request<MarketplaceOrg[]>("/marketplace/orgs/");
  }

  /** Create a developer org (`POST /marketplace/orgs/`). */
  createOrg(input: { name: string; plan_tier?: string }) {
    return this.request<MarketplaceOrg>("/marketplace/orgs/", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  /** Marketplace usage summary (`GET /marketplace/usage/`). */
  usage() {
    return this.request<MarketplaceUsage>("/marketplace/usage/");
  }

  /** Marketplace analytics (`GET /marketplace/analytics/`). */
  analytics(days = 30) {
    const qs = new URLSearchParams({ days: String(days) });
    return this.request<Record<string, unknown>>(
      `/marketplace/analytics/?${qs}`,
    );
  }
}

export default ToolVerseApiClient;
