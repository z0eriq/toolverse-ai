import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setTokens,
  type AuthTokens,
  type AuthUser,
} from "./auth";
import { getApiUrl } from "./utils";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  error?: { message?: unknown; status_code?: number };
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  auth?: boolean;
  skipRefresh?: boolean;
};

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refresh = getRefreshToken();
    if (!refresh) return null;

    try {
      const res = await fetch(`${getApiUrl()}/auth/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ refresh }),
      });

      if (!res.ok) {
        clearTokens();
        return null;
      }

      const json = (await res.json()) as { access?: string; data?: { access?: string } };
      const access = json.access ?? json.data?.access;
      if (!access) {
        clearTokens();
        return null;
      }
      setAccessToken(access);
      return access;
    } catch {
      clearTokens();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, auth = false, skipRefresh = false, headers, ...rest } = options;
  const url = path.startsWith("http") ? path : `${getApiUrl()}${path.startsWith("/") ? path : `/${path}`}`;

  const finalHeaders = new Headers(headers);
  if (!finalHeaders.has("Accept")) {
    finalHeaders.set("Accept", "application/json");
  }
  if (body !== undefined && !(body instanceof FormData)) {
    finalHeaders.set("Content-Type", "application/json");
  }

  if (auth) {
    const token = getAccessToken();
    if (token) finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  let response = await fetch(url, {
    ...rest,
    headers: finalHeaders,
    body:
      body === undefined
        ? undefined
        : body instanceof FormData
          ? body
          : JSON.stringify(body),
  });

  if (response.status === 401 && auth && !skipRefresh) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      finalHeaders.set("Authorization", `Bearer ${newAccess}`);
      response = await fetch(url, {
        ...rest,
        headers: finalHeaders,
        body:
          body === undefined
            ? undefined
            : body instanceof FormData
              ? body
              : JSON.stringify(body),
      });
    }
  }

  const text = await response.text();
  let parsed: unknown = null;
  if (text) {
    try {
      parsed = JSON.parse(text) as unknown;
    } catch {
      parsed = text;
    }
  }

  if (!response.ok) {
    const envelope = parsed as ApiEnvelope<unknown> | null;
    const message =
      (envelope && typeof envelope === "object" && envelope.error?.message
        ? typeof envelope.error.message === "string"
          ? envelope.error.message
          : JSON.stringify(envelope.error.message)
        : null) ||
      response.statusText ||
      "Request failed";
    throw new ApiError(message, response.status, parsed);
  }

  if (
    parsed &&
    typeof parsed === "object" &&
    "success" in parsed &&
    "data" in parsed
  ) {
    return (parsed as ApiEnvelope<T>).data;
  }

  return parsed as T;
}

export interface ToolListItem {
  id: number;
  tool_id: string;
  slug: string;
  category: string;
  name: Record<string, string> | string;
  description: Record<string, string> | string;
  version: string;
  premium: boolean;
  adsense_slot: string;
  icon: string;
  order: number;
  usage_count: number;
  capabilities: string[];
  source?: "filesystem" | "dynamic" | string;
}

export interface ToolFaqItem {
  question: string;
  answer: string;
}

export interface ToolHowToStep {
  name: string;
  text: string;
}

export interface ToolDetail extends ToolListItem {
  seo_title?: Record<string, string> | string;
  seo_description?: Record<string, string> | string;
  seo_keywords?: string[];
  schema_type?: string;
  faq?: ToolFaqItem[];
  howto_steps?: ToolHowToStep[];
  related_slugs?: string[];
  ui_schema?: DynamicUiSchema;
  created_at?: string;
  updated_at?: string;
}

export interface DynamicUiField {
  name: string;
  type?: "text" | "textarea" | "number" | "select" | "checkbox" | string;
  label?: string;
  placeholder?: string;
  required?: boolean;
  options?: { label: string; value: string }[];
  defaultValue?: string | number | boolean;
}

export interface DynamicUiSchema {
  fields?: DynamicUiField[];
  submitLabel?: string;
  [key: string]: unknown;
}

export interface CategoryItem {
  id: number;
  slug: string;
  name: Record<string, string> | string;
  description: Record<string, string> | string;
  order: number;
  is_active: boolean;
  tool_count?: number;
}

export interface HistoryItem {
  id: number;
  tool: ToolListItem;
  action: string;
  meta: Record<string, unknown>;
  created_at: string;
}

export interface FavoriteItem {
  id: number;
  tool: ToolListItem;
  created_at: string;
}

export interface BlogPostListItem {
  slug: string;
  title: string;
  excerpt: string;
  cover_image: string;
  published_at: string | null;
  tags: { slug: string; name: string }[];
  author_name: string;
  seo_title: string;
  seo_description: string;
}

export interface BlogPostDetail extends BlogPostListItem {
  content: string;
}

export interface PlanItem {
  slug: string;
  name: string;
  description: string;
  price_cents: number;
  currency: string;
  features: string[] | Record<string, unknown>;
  monthly_tool_runs?: number;
  api_monthly_quota?: number;
  ads_free?: boolean;
  history_days?: number;
}

export interface KeywordOpportunityItem {
  id: number;
  keyword: string;
  locale: string;
  search_volume: number;
  difficulty: number;
  ranking_position: number | null;
  ctr: number;
  clicks: number;
  impressions: number;
  suggested_tool_slug: string;
  priority_score: number;
  last_synced_at: string | null;
}

export interface ToolOpportunityItem {
  id: number;
  suggested_slug: string;
  category_slug: string;
  title: string;
  rationale: string;
  seo_score: number;
  demand_score: number;
  competition_score: number;
  value_score: number;
  priority_score: number;
  status: string;
  keyword_ids: number[];
  tool_spec: number | null;
}

export interface AutopilotRunItem {
  id: number;
  keyword: number | null;
  stage: string;
  status: string;
  content_item: number | null;
  quality_score: number | null;
  is_duplicate: boolean;
  error: string;
  meta: Record<string, unknown>;
}

export interface EmailCampaignItem {
  id: number;
  slug: string;
  subject: string;
  body_html: string;
  body_text: string;
  status: string;
  scheduled_at: string | null;
  sent_at: string | null;
}

export interface ExperimentItem {
  id: number;
  key: string;
  name: string;
  description: string;
  variants: { key?: string; weight?: number; id?: string; payload?: unknown }[];
  is_active: boolean;
}

export interface ExperimentAssignResult {
  key: string;
  subject_key: string;
  variant: string;
  assignment_id: number;
}

export interface DeveloperOrgItem {
  id: number;
  name: string;
  plan_tier: string;
}

export interface ApiInvoiceStubItem {
  id: number;
  org: number;
  period_start: string;
  period_end: string;
  amount_cents: number;
  usage_units: number;
  status: string;
}

export interface SeoHealthScoreItem {
  id: number;
  path: string;
  metadata: number;
  schema: number;
  internal_links: number;
  content_quality: number;
  keyword_coverage: number;
  performance: number;
  overall: number;
  recommendations: unknown[];
  analyzed_at: string | null;
}

export interface GrowthInsightItem {
  id: number;
  category: string;
  title: string;
  rationale: string;
  priority: number;
  status: string;
  meta: Record<string, unknown>;
}

export interface GrowthAgentRunItem {
  id: number;
  status: string;
  summary: string;
  insights_created: number;
  error: string;
  finished_at: string | null;
}

export interface WorkflowItem {
  id: number;
  name: string;
  slug: string;
  steps: Record<string, unknown>[];
  visibility: string;
  share_token: string;
}

export interface WorkflowTemplateItem {
  id: number;
  slug: string;
  name: string;
  description: string;
  steps: Record<string, unknown>[];
  category: string;
  is_public: boolean;
}

export interface WorkflowRunItem {
  id: number;
  status: string;
  input_payload?: Record<string, unknown>;
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  output_payload?: Record<string, unknown>;
  error?: string;
  duration_ms?: number;
}

export interface CommunityProfileItem {
  username: string;
  headline: string;
  bio: string;
  avatar_url?: string;
  collections?: CommunityCollectionItem[];
}

export interface CommunityCollectionItem {
  id?: number;
  name: string;
  public_slug: string;
  description: string;
  owner_username?: string;
  user?: number;
  items?: { tool_slug?: string; title?: string; tool?: { slug?: string } }[];
}

export interface CreatorProfileItem {
  id: number;
  display_name: string;
  bio: string;
  payout_ready: boolean;
}

export interface CreatorSubmissionItem {
  id: number;
  type: string;
  payload: Record<string, unknown>;
  tool_spec: number | null;
  tool_spec_slug: string | null;
  status: string;
  reviewer_notes: string;
}

export interface CommandCenterData {
  window_days: number;
  dau: number;
  mau: number;
  registrations: number;
  tool_executions: number;
  premium_conversions: number;
  revenue_cents: number;
  api_usage_units: number;
  seo_clicks: number;
  seo_impressions: number;
  countries: { country: string; count: number }[];
  top_tools: { tool_id: string; count: number }[];
  funnel?: {
    window_days: number;
    steps: { key: string; label: string; count: number }[];
    completion_rate: number;
    conversion_rate: number;
  };
  adsense_ready?: boolean;
  deploy_release?: string;
  open_campaigns?: number;
  indexed_urls_count?: number;
  draft_tool_specs_count?: number;
}

export interface ToolPerformanceScoreItem {
  id: number;
  tool: number;
  tool_slug?: string;
  traffic_score: number;
  usage_score: number;
  revenue_score: number;
  seo_score: number;
  retention_score: number;
  priority_score: number;
  computed_at: string | null;
}

export interface SeoOpportunityTaskItem {
  id: number;
  source: string;
  title: string;
  rationale: string;
  priority: number;
  status: string;
  suggested_action: string;
  path: string;
}

export interface GrowthTaskItem {
  id: number;
  title: string;
  category: string;
  priority: number;
  status: string;
  insight: number | null;
  meta: Record<string, unknown>;
}

export interface ReadinessCheckItem {
  id?: number;
  key: string;
  category: string;
  status: string;
  detail: string;
  checked_at?: string | null;
}

export interface SalesLeadItem {
  id: number;
  name: string;
  email: string;
  company: string;
  role: string;
  message: string;
  intent: string;
  status: string;
}

export interface ReferralMeData {
  code: string;
  link?: string;
  attributions?: number;
  rewards?: unknown[];
}

export interface GamificationMeData {
  balance: number;
  lifetime: number;
  level: number;
  badges?: { slug: string; name: string }[];
}

export interface BadgeItem {
  slug: string;
  name: string;
  description: string;
}

export interface ModerationQueueItem {
  type: string;
  id: number;
  status?: string;
  tool?: string;
  body?: string;
  rating?: number;
}

export interface AdminMetrics {
  users: number;
  tools: number;
  premium_tools: number;
  history_events: number;
  analytics_events: number;
  blog_posts: number;
  premium_subscribers: number;
  top_tools: { tool_id: string; slug: string; usage_count: number }[];
}

export interface SitemapTool {
  slug: string;
  category: string;
  updated_at: string;
  premium: boolean;
}

export interface AiCompleteBody {
  messages: { role: string; content: string }[];
  provider?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  tool_id?: string;
}

export interface AiCompleteResult {
  content: string;
  provider: string;
  model: string;
  tokens_in: number;
  tokens_out: number;
}

export interface AiUsageSummary {
  total_calls: number;
  by_provider: {
    provider: string;
    calls: number;
    tokens_in: number | null;
    tokens_out: number | null;
    cost: number | null;
  }[];
}

export type AsyncJobStatus = "queued" | "running" | "succeeded" | "failed";

export interface AsyncJob {
  id: string;
  tool_id: string;
  status: AsyncJobStatus;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  error: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface DynamicToolDefinition {
  id: number;
  slug: string;
  category_slug: string;
  name: Record<string, string> | string;
  description: Record<string, string> | string;
  version: string;
  revision: number;
  premium: boolean;
  status: "draft" | "published" | "archived" | string;
  ui_schema: DynamicUiSchema;
  pipeline: unknown[];
  seo: Record<string, unknown>;
  faq: ToolFaqItem[];
  howto_steps: ToolHowToStep[];
  capabilities: string[];
  icon: string;
  adsense_slot: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DynamicToolCreateInput {
  slug: string;
  category_slug: string;
  name: Record<string, string> | string;
  description?: Record<string, string> | string;
  version?: string;
  premium?: boolean;
  ui_schema?: DynamicUiSchema;
  pipeline?: unknown[];
  seo?: Record<string, unknown>;
  faq?: ToolFaqItem[];
  howto_steps?: ToolHowToStep[];
  capabilities?: string[];
  icon?: string;
  adsense_slot?: string;
  status?: string;
}

export interface DynamicToolRunResult {
  slug: string;
  output: unknown;
  vars?: Record<string, unknown>;
}

export interface AnalyticsDashboard {
  window_days: number;
  usage_series: { date: string; count: number }[];
  ctr: {
    impressions: number;
    clicks: number;
    uses: number;
    click_through_rate: number;
    use_rate: number;
  };
  retention: {
    cohort: number;
    d1: number;
    d7: number;
    d30: number;
  };
  geo: { country: string; count: number }[];
  top_tools: { tool_id: string; count: number }[];
  rollup_event_total: number;
}

export interface ApiKeyItem {
  id: number;
  name: string;
  key_prefix: string;
  scopes: string[];
  rate_limit_per_minute: number;
  monthly_quota: number;
  usage_this_month: number;
  revoked_at: string | null;
  last_used_at: string | null;
  created_at: string;
  /** Present only on create — shown once */
  key?: string;
}

export interface ApiKeyCreateInput {
  name: string;
  scopes?: string[];
  rate_limit_per_minute?: number;
  monthly_quota?: number;
}

export interface ApiUsageSummary {
  keys_total: number;
  keys_active: number;
  keys_revoked: number;
  usage_this_month: number;
  total_units: number;
  total_calls: number;
  by_endpoint: { endpoint: string; calls: number; units: number | null }[];
}

export interface ProgrammaticPageListItem {
  slug: string;
  path: string;
  path_pattern: string;
  title: Record<string, string> | string;
  description: Record<string, string> | string;
  page_type: string;
  topic: string;
  category_slug: string;
  audience: string;
  keyword: string;
  status: string;
  related_tool_ids: string[];
  seo_title: Record<string, string> | string;
  seo_description: Record<string, string> | string;
  updated_at: string;
}

export interface ProgrammaticPageDetail extends ProgrammaticPageListItem {
  body: Record<string, unknown> | string;
  seo_keywords: string[];
  created_at: string;
}

export interface ProgrammaticSitemapEntry {
  path: string;
  page_type: string;
  updated_at: string;
}

export interface SavedOutputItem {
  id: number;
  tool: number;
  tool_id?: string;
  tool_slug: string;
  title: string;
  content: unknown;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SavedOutputCreateInput {
  tool_id: string;
  title?: string;
  content?: unknown;
  meta?: Record<string, unknown>;
}

export interface CollectionItemRow {
  id: number;
  tool: number;
  tool_id?: string;
  tool_slug: string;
  order: number;
  created_at: string;
}

export interface ToolCollection {
  id: number;
  name: string;
  slug: string;
  description: string;
  items: CollectionItemRow[];
  created_at: string;
  updated_at: string;
}

export interface CollectionCreateInput {
  name: string;
  slug?: string;
  description?: string;
}

export interface ToolReviewItem {
  id: number;
  tool: number;
  tool_id?: string;
  tool_slug: string;
  rating: number;
  title: string;
  body: string;
  status: string;
  user_name: string;
  created_at: string;
}

export interface ToolReviewCreateInput {
  tool_id: string;
  rating: number;
  title?: string;
  body?: string;
}

export interface ToolCommentItem {
  id: number;
  tool: number;
  tool_id?: string;
  tool_slug: string;
  body: string;
  parent: number | null;
  status: string;
  user_name: string;
  created_at: string;
}

export interface ToolCommentCreateInput {
  tool_id: string;
  body: string;
  parent?: number | null;
}

export interface AssistantSuggestedCta {
  href: string;
  label: string;
}

export interface AssistantChatResult {
  reply: string;
  recommended_tools: {
    tool_id?: string;
    slug?: string;
    category?: string;
    name?: Record<string, string> | string;
    score?: number;
  }[];
  session_id?: number;
  meta?: {
    intent?: string;
    suggested_cta?: AssistantSuggestedCta;
    [key: string]: unknown;
  };
}

export interface GrowthActionItem {
  id: number;
  task: number | null;
  action_type: string;
  payload: Record<string, unknown>;
  status: string;
  result_ref: Record<string, unknown>;
  error: string;
  created_at: string;
  updated_at: string;
}

export interface SeoPageIssueItem {
  id: number;
  run: number | null;
  path: string;
  issue_type: string;
  severity: string;
  suggestion: string;
  status: string;
  evidence: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SeoAutopilotScanResult {
  id: number;
  status: string;
  issues_created: number;
  summary: string;
  error: string;
  finished_at: string | null;
}

export interface AdPerformanceDailyItem {
  id: number;
  date: string;
  placement_key: string;
  impressions: number;
  clicks: number;
  revenue_cents: number;
  ctr: number | string;
  rpm: number | string;
  created_at: string;
  updated_at: string;
}

export interface AdOptimizationRecItem {
  id: number;
  placement_key: string;
  title: string;
  rationale: string;
  priority: number;
  status: string;
  evidence: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CompetitorDomainItem {
  id: number;
  domain: string;
  name: string;
  is_active: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface CompetitorOpportunityItem {
  id: number;
  competitor: number;
  competitor_domain: string;
  keyword: string;
  title: string;
  rationale: string;
  gap_score: number;
  status: string;
  evidence: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface BacklinkTargetItem {
  id: number;
  url: string;
  path: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BacklinkCampaignItem {
  id: number;
  name: string;
  target: number | null;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface BacklinkOpportunityItem {
  id: number;
  campaign: number | null;
  target: number | null;
  source_domain: string;
  source_url: string;
  contact_email: string;
  priority: number;
  status: string;
  rationale: string;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface MobileToolItem {
  slug: string;
  category: string;
  name: Record<string, string> | string;
  tool_id?: string;
  icon?: string;
}

export interface GrowthDashboard {
  window_days: number;
  search_impressions: number;
  tool_views: number;
  tool_usage: number;
  conversion_rate: number;
  returning_users: {
    total_actors: number;
    returning_actors: number;
    returning_rate: number;
  };
  languages: { locale: string; count: number }[];
  traffic_sources: { host: string; count: number }[];
}

export interface ContentItem {
  id: number;
  title: string;
  slug: string;
  body: string;
  content_type: string;
  status: string;
  locale: string;
  tool: number | null;
  target_path: string;
  meta_title: string;
  meta_description: string;
  created_by: number | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromptTemplateItem {
  id: number;
  slug: string;
  name: string;
  template_text: string;
  purpose: string;
  locale: string;
  created_at: string;
  updated_at: string;
}

export interface ToolSpecItem {
  id: number;
  slug: string;
  category_slug: string;
  name: Record<string, string> | string;
  description: Record<string, string> | string;
  ui_schema: DynamicUiSchema | Record<string, unknown>;
  pipeline: unknown[];
  seo: Record<string, unknown>;
  faq: ToolFaqItem[];
  howto: ToolHowToStep[];
  capabilities: string[];
  recipe: string;
  status: string;
  error: string;
  is_viral: boolean;
  share_text: Record<string, string> | Record<string, unknown>;
  export_filesystem: boolean;
  created_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface ToolSpecCreateInput {
  slug: string;
  category_slug?: string;
  name: Record<string, string> | string;
  description?: Record<string, string> | string;
  recipe?: string;
  ui_schema?: DynamicUiSchema | Record<string, unknown>;
  pipeline?: unknown[];
  seo?: Record<string, unknown>;
  faq?: ToolFaqItem[];
  howto?: ToolHowToStep[];
  capabilities?: string[];
  is_viral?: boolean;
  share_text?: Record<string, string> | Record<string, unknown>;
  export_filesystem?: boolean;
}

export interface AdPlacementItem {
  id: number;
  key: string;
  enabled: boolean;
  network: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AffiliateLinkItem {
  id: number;
  tool: number | null;
  tool_slug: string | null;
  label: string;
  destination_url: string;
  network: string;
  utm: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SponsoredToolItem {
  id: number;
  tool: number;
  tool_slug: string;
  sponsor_name: string;
  start_at: string | null;
  end_at: string | null;
  priority: number;
  creative: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RevenueSummary {
  by_type: { type: string; total_cents: number | null; count: number }[];
  total_cents: number;
  event_count: number;
  placements: number;
  sponsored_active: number;
  affiliates_active: number;
}

export interface GscOverview {
  days: number;
  clicks: number;
  impressions: number;
  avg_ctr: number;
  avg_position: number;
  row_count: number;
}

export interface GscQueryRow {
  query: string;
  clicks: number | null;
  impressions: number | null;
  avg_ctr: number | null;
  avg_position: number | null;
}

export interface GscPageRow {
  page: string;
  clicks: number | null;
  impressions: number | null;
  avg_ctr: number | null;
  avg_position: number | null;
}

export interface SeoRecommendationItem {
  id: number;
  path: string;
  tool: number | null;
  tool_slug: string | null;
  type: string;
  severity: string;
  suggestion: string;
  rationale: string;
  status: string;
  evidence: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PushSubscribeResult {
  id: number;
  created: boolean;
  endpoint: string;
}

export interface ToolsGrowthSnapshot {
  metrics: AdminMetrics;
  categories: CategoryItem[];
}

export const api = {
  login(email: string, password: string) {
    return apiRequest<AuthTokens & { user?: AuthUser }>("/auth/login/", {
      method: "POST",
      body: { email, password },
    });
  },

  async register(input: { email: string; name: string; password: string }) {
    return apiRequest<{ user: AuthUser; tokens: AuthTokens }>("/auth/register/", {
      method: "POST",
      body: input,
    });
  },

  me() {
    return apiRequest<AuthUser>("/auth/me/", { auth: true });
  },

  logout(refresh: string) {
    return apiRequest<{ detail: string }>("/auth/logout/", {
      method: "POST",
      auth: true,
      body: { refresh },
      skipRefresh: true,
    });
  },

  categories() {
    return apiRequest<CategoryItem[]>("/categories/");
  },

  tools(params?: { q?: string; category?: string }) {
    const search = new URLSearchParams();
    if (params?.q) search.set("q", params.q);
    if (params?.category) search.set("category", params.category);
    const qs = search.toString();
    return apiRequest<ToolListItem[] | { results: ToolListItem[] }>(
      `/tools/${qs ? `?${qs}` : ""}`,
    );
  },

  tool(slug: string) {
    return apiRequest<ToolDetail>(`/tools/${slug}/`);
  },

  relatedTools(slug: string, limit = 6) {
    const qs = new URLSearchParams({ limit: String(limit) });
    return apiRequest<ToolListItem[]>(`/tools/${slug}/related/?${qs}`);
  },

  trackTool(slug: string) {
    return apiRequest<{ tracked: boolean }>(`/tools/${slug}/track/`, {
      method: "POST",
    });
  },

  sitemapTools() {
    return apiRequest<SitemapTool[]>("/sitemap/tools/");
  },

  favorites() {
    return apiRequest<FavoriteItem[]>("/favorites/", { auth: true });
  },

  addFavorite(toolId: string) {
    return apiRequest<FavoriteItem>("/favorites/", {
      method: "POST",
      auth: true,
      body: { tool_id: toolId },
    });
  },

  removeFavorite(toolId: string) {
    return apiRequest<{ deleted: boolean }>(`/favorites/${toolId}/`, {
      method: "DELETE",
      auth: true,
    });
  },

  history() {
    return apiRequest<HistoryItem[]>("/history/", { auth: true });
  },

  recordHistory(toolId: string, action = "run", meta: Record<string, unknown> = {}) {
    return apiRequest<HistoryItem>("/history/", {
      method: "POST",
      auth: true,
      body: { tool_id: toolId, action, meta },
    });
  },

  plans() {
    return apiRequest<PlanItem[]>("/subscriptions/plans/");
  },

  blogPosts() {
    return apiRequest<BlogPostListItem[] | { results: BlogPostListItem[] }>("/blog/");
  },

  blogPost(slug: string) {
    return apiRequest<BlogPostDetail>(`/blog/${slug}/`);
  },

  adminMetrics() {
    return apiRequest<AdminMetrics>("/admin/metrics/", { auth: true });
  },

  trackEvent(input: {
    name: string;
    session_id?: string;
    path?: string;
    properties?: Record<string, unknown>;
    tool_id?: string;
    utm_source?: string;
    utm_medium?: string;
    utm_campaign?: string;
    campaign_key?: string;
  }) {
    return apiRequest<{ id: number }>("/analytics/track/", {
      method: "POST",
      body: input,
      auth: Boolean(getAccessToken()),
    });
  },

  aiComplete(body: AiCompleteBody) {
    return apiRequest<AiCompleteResult>("/ai/complete/", {
      method: "POST",
      auth: true,
      body,
    });
  },

  aiUsage() {
    return apiRequest<AiUsageSummary>("/ai/usage/", { auth: true });
  },

  createJob(tool_id: string, input: Record<string, unknown> = {}) {
    return apiRequest<AsyncJob>("/jobs/", {
      method: "POST",
      auth: true,
      body: { tool_id, input },
    });
  },

  getJob(id: string) {
    return apiRequest<AsyncJob>(`/jobs/${id}/`, { auth: true });
  },

  listDynamicTools() {
    return apiRequest<DynamicToolDefinition[]>("/admin/tools/dynamic/", {
      auth: true,
    });
  },

  createDynamicTool(input: DynamicToolCreateInput) {
    return apiRequest<DynamicToolDefinition>("/admin/tools/dynamic/", {
      method: "POST",
      auth: true,
      body: input,
    });
  },

  updateDynamicTool(id: number, input: Partial<DynamicToolCreateInput>) {
    return apiRequest<DynamicToolDefinition>(`/admin/tools/dynamic/${id}/`, {
      method: "PATCH",
      auth: true,
      body: input,
    });
  },

  publishDynamicTool(id: number) {
    return apiRequest<{
      definition: DynamicToolDefinition;
      tool: ToolDetail;
    }>(`/admin/tools/dynamic/${id}/publish/`, {
      method: "POST",
      auth: true,
    });
  },

  async runDynamicTool(slug: string, input: Record<string, unknown>) {
    try {
      return await apiRequest<DynamicToolRunResult>(`/t/dynamic/${slug}/run/`, {
        method: "POST",
        body: { input },
        auth: Boolean(getAccessToken()),
      });
    } catch (err) {
      if (err instanceof ApiError && (err.status === 404 || err.status === 405)) {
        return apiRequest<DynamicToolRunResult>(`/dynamic/${slug}/run/`, {
          method: "POST",
          body: { input },
          auth: Boolean(getAccessToken()),
        });
      }
      throw err;
    }
  },

  analyticsDashboard() {
    return apiRequest<AnalyticsDashboard>("/analytics/dashboard/", {
      auth: true,
    });
  },

  listApiKeys() {
    return apiRequest<ApiKeyItem[]>("/marketplace/keys/", { auth: true });
  },

  createApiKey(input: ApiKeyCreateInput) {
    return apiRequest<ApiKeyItem>("/marketplace/keys/", {
      method: "POST",
      auth: true,
      body: input,
    });
  },

  revokeApiKey(id: number) {
    return apiRequest<ApiKeyItem>(`/marketplace/keys/${id}/revoke/`, {
      method: "POST",
      auth: true,
    });
  },

  apiUsage() {
    return apiRequest<ApiUsageSummary>("/marketplace/usage/", { auth: true });
  },

  programmaticList(params?: {
    page_type?: string;
    category_slug?: string;
    topic?: string;
    audience?: string;
    q?: string;
  }) {
    const search = new URLSearchParams();
    if (params?.page_type) search.set("page_type", params.page_type);
    if (params?.category_slug) search.set("category_slug", params.category_slug);
    if (params?.topic) search.set("topic", params.topic);
    if (params?.audience) search.set("audience", params.audience);
    if (params?.q) search.set("search", params.q);
    const qs = search.toString();
    return apiRequest<
      ProgrammaticPageListItem[] | { results: ProgrammaticPageListItem[] }
    >(`/programmatic/${qs ? `?${qs}` : ""}`);
  },

  programmaticByPath(path: string) {
    const qs = new URLSearchParams({ path: path.replace(/^\/+/, "") });
    return apiRequest<ProgrammaticPageDetail>(`/programmatic/by-path/?${qs}`);
  },

  programmaticSitemap() {
    return apiRequest<ProgrammaticSitemapEntry[]>("/programmatic/sitemap/");
  },

  contentList(params?: { status?: string; locale?: string; content_type?: string }) {
    const search = new URLSearchParams();
    if (params?.status) search.set("status", params.status);
    if (params?.locale) search.set("locale", params.locale);
    if (params?.content_type) search.set("content_type", params.content_type);
    const qs = search.toString();
    return apiRequest<ContentItem[] | { results: ContentItem[] }>(
      `/admin/content/${qs ? `?${qs}` : ""}`,
      { auth: true },
    );
  },

  contentDetail(id: number) {
    return apiRequest<ContentItem>(`/admin/content/${id}/`, { auth: true });
  },

  contentPublish(id: number) {
    return apiRequest<ContentItem>(`/admin/content/${id}/publish/`, {
      method: "POST",
      auth: true,
    });
  },

  contentRegenerate(id: number) {
    return apiRequest<ContentItem>(`/admin/content/${id}/regenerate/`, {
      method: "POST",
      auth: true,
    });
  },

  contentTemplates() {
    return apiRequest<PromptTemplateItem[] | { results: PromptTemplateItem[] }>(
      "/admin/content/templates/",
      { auth: true },
    );
  },

  savedOutputs() {
    return apiRequest<SavedOutputItem[]>("/engagement/saved-outputs/", {
      auth: true,
    });
  },

  createSavedOutput(input: SavedOutputCreateInput) {
    return apiRequest<SavedOutputItem>("/engagement/saved-outputs/", {
      method: "POST",
      auth: true,
      body: input,
    });
  },

  updateSavedOutput(id: number, input: Partial<SavedOutputCreateInput>) {
    return apiRequest<SavedOutputItem>(`/engagement/saved-outputs/${id}/`, {
      method: "PATCH",
      auth: true,
      body: input,
    });
  },

  deleteSavedOutput(id: number) {
    return apiRequest<{ deleted: boolean }>(`/engagement/saved-outputs/${id}/`, {
      method: "DELETE",
      auth: true,
    });
  },

  collections() {
    return apiRequest<ToolCollection[]>("/engagement/collections/", {
      auth: true,
    });
  },

  createCollection(input: CollectionCreateInput) {
    return apiRequest<ToolCollection>("/engagement/collections/", {
      method: "POST",
      auth: true,
      body: input,
    });
  },

  collection(slug: string) {
    return apiRequest<ToolCollection>(`/engagement/collections/${slug}/`, {
      auth: true,
    });
  },

  updateCollection(slug: string, input: Partial<CollectionCreateInput>) {
    return apiRequest<ToolCollection>(`/engagement/collections/${slug}/`, {
      method: "PATCH",
      auth: true,
      body: input,
    });
  },

  deleteCollection(slug: string) {
    return apiRequest<{ deleted: boolean }>(`/engagement/collections/${slug}/`, {
      method: "DELETE",
      auth: true,
    });
  },

  addCollectionItem(slug: string, tool_id: string, order = 0) {
    return apiRequest<CollectionItemRow>(`/engagement/collections/${slug}/items/`, {
      method: "POST",
      auth: true,
      body: { tool_id, order },
    });
  },

  removeCollectionItem(slug: string, tool_id: string) {
    return apiRequest<{ deleted: boolean }>(
      `/engagement/collections/${slug}/items/${tool_id}/`,
      { method: "DELETE", auth: true },
    );
  },

  reviews(params?: { tool?: string }) {
    const search = new URLSearchParams();
    if (params?.tool) search.set("tool", params.tool);
    const qs = search.toString();
    return apiRequest<ToolReviewItem[]>(
      `/engagement/reviews/${qs ? `?${qs}` : ""}`,
    );
  },

  createReview(input: ToolReviewCreateInput) {
    return apiRequest<ToolReviewItem>("/engagement/reviews/", {
      method: "POST",
      auth: true,
      body: input,
    });
  },

  moderateReview(id: number, status: string) {
    return apiRequest<ToolReviewItem>(`/engagement/reviews/${id}/moderate/`, {
      method: "POST",
      auth: true,
      body: { status },
    });
  },

  comments(params?: { tool?: string }) {
    const search = new URLSearchParams();
    if (params?.tool) search.set("tool", params.tool);
    const qs = search.toString();
    return apiRequest<ToolCommentItem[]>(
      `/engagement/comments/${qs ? `?${qs}` : ""}`,
    );
  },

  createComment(input: ToolCommentCreateInput) {
    return apiRequest<ToolCommentItem>("/engagement/comments/", {
      method: "POST",
      auth: true,
      body: input,
    });
  },

  moderateComment(id: number, status: string) {
    return apiRequest<ToolCommentItem>(`/engagement/comments/${id}/moderate/`, {
      method: "POST",
      auth: true,
      body: { status },
    });
  },

  assistantChat(input: {
    message: string;
    session_id?: number;
    persist?: boolean;
    session_key?: string;
    locale?: string;
  }) {
    return apiRequest<AssistantChatResult>("/assistant/chat/", {
      method: "POST",
      body: input,
      auth: Boolean(getAccessToken()),
    });
  },

  growthDashboard() {
    return apiRequest<GrowthDashboard>("/analytics/growth/", { auth: true });
  },

  toolFactory: {
    listSpecs(params?: { status?: string; recipe?: string; category_slug?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      if (params?.recipe) search.set("recipe", params.recipe);
      if (params?.category_slug) search.set("category_slug", params.category_slug);
      const qs = search.toString();
      return apiRequest<ToolSpecItem[] | { results: ToolSpecItem[] }>(
        `/admin/tool-factory/specs/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    createSpec(input: ToolSpecCreateInput) {
      return apiRequest<ToolSpecItem>("/admin/tool-factory/specs/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },

    updateSpec(id: number, input: Partial<ToolSpecCreateInput>) {
      return apiRequest<ToolSpecItem>(`/admin/tool-factory/specs/${id}/`, {
        method: "PATCH",
        auth: true,
        body: input,
      });
    },

    buildSpec(id: number, opts?: { async?: boolean }) {
      return apiRequest<Record<string, unknown>>(
        `/admin/tool-factory/specs/${id}/build/`,
        {
          method: "POST",
          auth: true,
          body: opts?.async ? { async: true } : {},
        },
      );
    },

    publishSpec(id: number) {
      return apiRequest<Record<string, unknown>>(
        `/admin/tool-factory/specs/${id}/publish/`,
        {
          method: "POST",
          auth: true,
          body: {},
        },
      );
    },
  },

  monetization: {
    placements() {
      return apiRequest<AdPlacementItem[]>("/monetization/placements/");
    },

    affiliates(toolId?: string) {
      const search = new URLSearchParams();
      if (toolId) search.set("tool_id", toolId);
      const qs = search.toString();
      return apiRequest<AffiliateLinkItem[]>(
        `/monetization/affiliates/${qs ? `?${qs}` : ""}`,
      );
    },

    sponsored() {
      return apiRequest<SponsoredToolItem[]>("/monetization/sponsored/");
    },
  },

  adminRevenue: {
    summary() {
      return apiRequest<RevenueSummary>("/admin/revenue/summary/", {
        auth: true,
      });
    },

    placements() {
      return apiRequest<AdPlacementItem[]>("/admin/revenue/placements/", {
        auth: true,
      });
    },

    createPlacement(input: Partial<AdPlacementItem>) {
      return apiRequest<AdPlacementItem>("/admin/revenue/placements/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },

    updatePlacement(id: number, input: Partial<AdPlacementItem>) {
      return apiRequest<AdPlacementItem>(`/admin/revenue/placements/${id}/`, {
        method: "PATCH",
        auth: true,
        body: input,
      });
    },

    deletePlacement(id: number) {
      return apiRequest<{ deleted: boolean }>(`/admin/revenue/placements/${id}/`, {
        method: "DELETE",
        auth: true,
      });
    },

    sponsored() {
      return apiRequest<SponsoredToolItem[]>("/admin/revenue/sponsored/", {
        auth: true,
      });
    },

    affiliates() {
      return apiRequest<AffiliateLinkItem[]>("/admin/revenue/affiliates/", {
        auth: true,
      });
    },
  },

  gsc: {
    overview(days = 28) {
      const qs = new URLSearchParams({ days: String(days) });
      return apiRequest<GscOverview>(`/admin/gsc/overview/?${qs}`, {
        auth: true,
      });
    },

    queries(params?: { days?: number; limit?: number }) {
      const search = new URLSearchParams();
      search.set("days", String(params?.days ?? 28));
      search.set("limit", String(params?.limit ?? 50));
      return apiRequest<GscQueryRow[]>(`/admin/gsc/queries/?${search}`, {
        auth: true,
      });
    },

    pages(params?: { days?: number; limit?: number }) {
      const search = new URLSearchParams();
      search.set("days", String(params?.days ?? 28));
      search.set("limit", String(params?.limit ?? 50));
      return apiRequest<GscPageRow[]>(`/admin/gsc/pages/?${search}`, {
        auth: true,
      });
    },
  },

  seo: {
    analyze(path: string) {
      return apiRequest<SeoRecommendationItem[]>("/admin/seo/analyze/", {
        method: "POST",
        auth: true,
        body: { path },
      });
    },

    recommendations(params?: { status?: string; type?: string; path?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      if (params?.type) search.set("type", params.type);
      if (params?.path) search.set("path", params.path);
      const qs = search.toString();
      return apiRequest<SeoRecommendationItem[] | { results: SeoRecommendationItem[] }>(
        `/admin/seo/recommendations/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    acceptRec(id: number) {
      return apiRequest<SeoRecommendationItem>(
        `/admin/seo/recommendations/${id}/accept/`,
        { method: "POST", auth: true },
      );
    },

    dismissRec(id: number) {
      return apiRequest<SeoRecommendationItem>(
        `/admin/seo/recommendations/${id}/dismiss/`,
        { method: "POST", auth: true },
      );
    },

    scanAutopilot() {
      return apiRequest<SeoAutopilotScanResult>("/admin/seo/autopilot/scan/", {
        method: "POST",
        auth: true,
        body: {},
      });
    },

    listIssues(params?: { status?: string; issue_type?: string; path?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      if (params?.issue_type) search.set("issue_type", params.issue_type);
      if (params?.path) search.set("path", params.path);
      const qs = search.toString();
      return apiRequest<SeoPageIssueItem[]>(
        `/admin/seo/issues/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    applyIssue(id: number) {
      return apiRequest<SeoPageIssueItem>(`/admin/seo/issues/${id}/apply/`, {
        method: "POST",
        auth: true,
        body: {},
      });
    },

    dismissIssue(id: number) {
      return apiRequest<SeoPageIssueItem>(`/admin/seo/issues/${id}/dismiss/`, {
        method: "POST",
        auth: true,
        body: {},
      });
    },
  },

  pushSubscribe(subscription: Record<string, unknown>) {
    return apiRequest<PushSubscribeResult>("/push/subscribe/", {
      method: "POST",
      auth: true,
      body: subscription,
    });
  },

  async toolsGrowth(): Promise<ToolsGrowthSnapshot> {
    const [metrics, categories] = await Promise.all([
      apiRequest<AdminMetrics>("/admin/metrics/", { auth: true }),
      apiRequest<CategoryItem[]>("/categories/"),
    ]);
    return {
      metrics,
      categories: Array.isArray(categories) ? categories : [],
    };
  },

  keywords: {
    list(params?: { limit?: number }) {
      const search = new URLSearchParams();
      if (params?.limit) search.set("limit", String(params.limit));
      const qs = search.toString();
      return apiRequest<KeywordOpportunityItem[]>(
        `/admin/keywords/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },
    top(limit = 50) {
      const qs = new URLSearchParams({ limit: String(limit) });
      return apiRequest<KeywordOpportunityItem[]>(
        `/admin/keywords/top/?${qs}`,
        { auth: true },
      );
    },
  },

  opportunities: {
    list() {
      return apiRequest<ToolOpportunityItem[]>("/admin/opportunities/", {
        auth: true,
      });
    },
    queue(id: number) {
      return apiRequest<ToolOpportunityItem>(
        `/admin/opportunities/${id}/queue/`,
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  autopilot: {
    listRuns() {
      return apiRequest<AutopilotRunItem[]>("/admin/autopilot/runs/", {
        auth: true,
      });
    },
    startRun(keywordId: number, opts?: { async_mode?: boolean }) {
      return apiRequest<AutopilotRunItem | { run: AutopilotRunItem }>(
        "/admin/autopilot/runs/",
        {
          method: "POST",
          auth: true,
          body: {
            keyword_id: keywordId,
            async_mode: opts?.async_mode ?? false,
          },
        },
      );
    },
    approve(id: number) {
      return apiRequest<AutopilotRunItem>(
        `/admin/autopilot/runs/${id}/approve/`,
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  newsletter: {
    subscribe(email: string, locale = "en") {
      return apiRequest<{ id: number; email: string }>("/newsletter/subscribe/", {
        method: "POST",
        body: { email, locale, source: "web" },
      });
    },
  },

  email: {
    campaigns() {
      return apiRequest<EmailCampaignItem[]>("/admin/email/campaigns/", {
        auth: true,
      });
    },
    createCampaign(input: {
      slug: string;
      subject: string;
      body_html: string;
      body_text?: string;
      status?: string;
    }) {
      return apiRequest<EmailCampaignItem>("/admin/email/campaigns/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },
    sendTest(id: number, email: string) {
      return apiRequest<Record<string, unknown>>(
        `/admin/email/campaigns/${id}/send-test/`,
        { method: "POST", auth: true, body: { email } },
      );
    },
  },

  experiments: {
    assign(key: string, subjectKey?: string) {
      const search = new URLSearchParams({ key });
      if (subjectKey) search.set("subject_key", subjectKey);
      return apiRequest<ExperimentAssignResult>(
        `/experiments/assign/?${search}`,
      );
    },
    track(input: {
      key: string;
      subject_key: string;
      event_name: string;
      properties?: Record<string, unknown>;
    }) {
      return apiRequest<Record<string, unknown>>("/experiments/track/", {
        method: "POST",
        body: input,
      });
    },
    adminList() {
      return apiRequest<ExperimentItem[]>("/admin/experiments/", {
        auth: true,
      });
    },
    adminResults(id: number) {
      return apiRequest<Record<string, unknown>>(
        `/admin/experiments/${id}/results/`,
        { auth: true },
      );
    },
  },

  marketplace: {
    analytics(days = 30) {
      const qs = new URLSearchParams({ days: String(days) });
      return apiRequest<{ days: number; daily: { day: string; calls: number; units: number }[] }>(
        `/marketplace/analytics/?${qs}`,
        { auth: true },
      );
    },
    orgs() {
      return apiRequest<DeveloperOrgItem[]>("/marketplace/orgs/", {
        auth: true,
      });
    },
    createOrg(input: { name: string; plan_tier?: string }) {
      return apiRequest<DeveloperOrgItem>("/marketplace/orgs/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },
    adminInvoices() {
      return apiRequest<ApiInvoiceStubItem[]>("/admin/marketplace/invoices/", {
        auth: true,
      });
    },
  },

  seoHealth: {
    list() {
      return apiRequest<SeoHealthScoreItem[]>("/admin/seo/health/", { auth: true });
    },
    analyze(path: string, perf?: number) {
      return apiRequest<SeoHealthScoreItem>("/admin/seo/health/", {
        method: "POST",
        auth: true,
        body: { path, perf },
      });
    },
    recompute() {
      return apiRequest<Record<string, unknown>>("/admin/seo/health/recompute/", {
        method: "POST",
        auth: true,
        body: {},
      });
    },
  },

  growthAgent: {
    runs() {
      return apiRequest<GrowthAgentRunItem[]>("/admin/growth-agent/runs/", {
        auth: true,
      });
    },
    startRun() {
      return apiRequest<GrowthAgentRunItem>("/admin/growth-agent/runs/", {
        method: "POST",
        auth: true,
        body: {},
      });
    },
    insights() {
      return apiRequest<GrowthInsightItem[]>("/admin/growth-agent/insights/", {
        auth: true,
      });
    },
    acceptInsight(id: number) {
      return apiRequest<GrowthInsightItem>(
        `/admin/growth-agent/insights/${id}/accept/`,
        { method: "POST", auth: true, body: {} },
      );
    },
    dismissInsight(id: number) {
      return apiRequest<GrowthInsightItem>(
        `/admin/growth-agent/insights/${id}/dismiss/`,
        { method: "POST", auth: true, body: {} },
      );
    },

    listActions(params?: { status?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      const qs = search.toString();
      return apiRequest<GrowthActionItem[]>(
        `/admin/growth-agent/actions/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    approveAction(id: number) {
      return apiRequest<GrowthActionItem>(
        `/admin/growth-agent/actions/${id}/approve/`,
        { method: "POST", auth: true, body: {} },
      );
    },

    rejectAction(id: number) {
      return apiRequest<GrowthActionItem>(
        `/admin/growth-agent/actions/${id}/reject/`,
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  revenue: {
    adPerformance() {
      return apiRequest<AdPerformanceDailyItem[]>(
        "/admin/revenue/ad-performance/",
        { auth: true },
      );
    },

    adRecommendations(params?: { status?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      const qs = search.toString();
      return apiRequest<AdOptimizationRecItem[]>(
        `/admin/revenue/ad-recommendations/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    generateAdRecommendations() {
      return apiRequest<{
        created: number;
        recommendations: AdOptimizationRecItem[];
      }>("/admin/revenue/ad-recommendations/", {
        method: "POST",
        auth: true,
        body: {},
      });
    },

    acceptAdRec(id: number) {
      return apiRequest<AdOptimizationRecItem>(
        `/admin/revenue/ad-recommendations/${id}/accept/`,
        { method: "POST", auth: true, body: {} },
      );
    },

    dismissAdRec(id: number) {
      return apiRequest<AdOptimizationRecItem>(
        `/admin/revenue/ad-recommendations/${id}/dismiss/`,
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  competitors: {
    listDomains() {
      return apiRequest<CompetitorDomainItem[]>("/admin/competitors/domains/", {
        auth: true,
      });
    },

    createDomain(input: {
      domain: string;
      name?: string;
      is_active?: boolean;
      notes?: string;
    }) {
      return apiRequest<CompetitorDomainItem>("/admin/competitors/domains/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },

    listOpportunities(params?: { status?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      const qs = search.toString();
      return apiRequest<CompetitorOpportunityItem[]>(
        `/admin/competitors/opportunities/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    recompute() {
      return apiRequest<Record<string, unknown>>(
        "/admin/competitors/recompute/",
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  backlinks: {
    listTargets() {
      return apiRequest<BacklinkTargetItem[]>("/admin/backlinks/targets/", {
        auth: true,
      });
    },

    listCampaigns() {
      return apiRequest<BacklinkCampaignItem[]>("/admin/backlinks/campaigns/", {
        auth: true,
      });
    },

    listOpportunities(params?: { status?: string }) {
      const search = new URLSearchParams();
      if (params?.status) search.set("status", params.status);
      const qs = search.toString();
      return apiRequest<BacklinkOpportunityItem[]>(
        `/admin/backlinks/opportunities/${qs ? `?${qs}` : ""}`,
        { auth: true },
      );
    },

    updateOpportunityStatus(id: number, status: string) {
      return apiRequest<BacklinkOpportunityItem>(
        `/admin/backlinks/opportunities/${id}/status/`,
        { method: "POST", auth: true, body: { status } },
      );
    },
  },

  mobile: {
    listTools(params?: { compact?: boolean }) {
      const qs = params?.compact ? "?compact=1" : "";
      return apiRequest<MobileToolItem[]>(`/mobile/tools/${qs}`);
    },
  },

  workflows: {
    list() {
      return apiRequest<WorkflowItem[]>("/workflows/", { auth: true });
    },
    create(input: {
      name: string;
      steps: Record<string, unknown>[];
      visibility?: string;
      slug?: string;
    }) {
      return apiRequest<WorkflowItem>("/workflows/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },
    get(id: number) {
      return apiRequest<WorkflowItem>(`/workflows/${id}/`, { auth: true });
    },
    update(id: number, input: Partial<WorkflowItem>) {
      return apiRequest<WorkflowItem>(`/workflows/${id}/`, {
        method: "PATCH",
        auth: true,
        body: input,
      });
    },
    remove(id: number) {
      return apiRequest<{ deleted?: boolean }>(`/workflows/${id}/`, {
        method: "DELETE",
        auth: true,
      });
    },
    run(id: number, input: Record<string, unknown>) {
      return apiRequest<WorkflowRunItem>(`/workflows/${id}/run/`, {
        method: "POST",
        auth: true,
        body: { input },
      });
    },
    shared(token: string) {
      return apiRequest<WorkflowItem>(`/workflows/shared/${token}/`);
    },
    templates() {
      return apiRequest<WorkflowTemplateItem[]>("/workflows/templates/");
    },
    usage() {
      return apiRequest<Record<string, unknown>>("/workflows/usage/", {
        auth: true,
      });
    },
    adminTemplates() {
      return apiRequest<WorkflowTemplateItem[]>("/admin/workflows/templates/", {
        auth: true,
      });
    },
  },

  community: {
    profile(username: string) {
      return apiRequest<CommunityProfileItem>(
        `/community/profiles/${encodeURIComponent(username)}/`,
      );
    },
    collections() {
      return apiRequest<CommunityCollectionItem[]>("/community/collections/");
    },
    collection(slug: string) {
      return apiRequest<CommunityCollectionItem>(
        `/community/collections/${encodeURIComponent(slug)}/`,
      );
    },
  },

  moderation: {
    queue() {
      return apiRequest<{
        reviews: ModerationQueueItem[];
        comments: ModerationQueueItem[];
      }>("/admin/moderation/queue/", { auth: true });
    },
  },

  creator: {
    profile() {
      return apiRequest<CreatorProfileItem>("/creator/profile/", { auth: true });
    },
    updateProfile(input: { display_name?: string; bio?: string }) {
      return apiRequest<CreatorProfileItem>("/creator/profile/", {
        method: "PATCH",
        auth: true,
        body: input,
      });
    },
    submissions() {
      return apiRequest<CreatorSubmissionItem[]>("/creator/submissions/", {
        auth: true,
      });
    },
    createSubmission(input: { type: string; payload: Record<string, unknown> }) {
      return apiRequest<CreatorSubmissionItem>("/creator/submissions/", {
        method: "POST",
        auth: true,
        body: input,
      });
    },
    submitForReview(id: number) {
      return apiRequest<CreatorSubmissionItem>(
        `/creator/submissions/${id}/submit/`,
        { method: "POST", auth: true, body: {} },
      );
    },
    adminSubmissions() {
      return apiRequest<CreatorSubmissionItem[]>("/admin/creator/submissions/", {
        auth: true,
      });
    },
    approve(id: number) {
      return apiRequest<CreatorSubmissionItem>(
        `/admin/creator/submissions/${id}/approve/`,
        { method: "POST", auth: true, body: {} },
      );
    },
    reject(id: number, notes?: string) {
      return apiRequest<CreatorSubmissionItem>(
        `/admin/creator/submissions/${id}/reject/`,
        { method: "POST", auth: true, body: { reviewer_notes: notes || "" } },
      );
    },
    usage() {
      return apiRequest<Record<string, unknown>[]>("/creator/usage/", {
        auth: true,
      });
    },
    payouts() {
      return apiRequest<Record<string, unknown>[]>("/creator/payouts/", {
        auth: true,
      });
    },
    adminRollup() {
      return apiRequest<Record<string, unknown>>("/admin/creator/rollup/", {
        method: "POST",
        auth: true,
        body: {},
      });
    },
  },

  commandCenter(days = 30) {
    const qs = new URLSearchParams({ days: String(days) });
    return apiRequest<CommandCenterData>(`/admin/command-center/?${qs}`, {
      auth: true,
    });
  },

  toolScores() {
    return apiRequest<ToolPerformanceScoreItem[]>("/admin/tool-scores/", {
      auth: true,
    });
  },

  seoOpportunityTasks: {
    list() {
      return apiRequest<SeoOpportunityTaskItem[]>(
        "/admin/seo/opportunity-tasks/",
        { auth: true },
      );
    },
    generate() {
      return apiRequest<Record<string, unknown>>(
        "/admin/seo/opportunity-tasks/generate/",
        { method: "POST", auth: true, body: {} },
      );
    },
    update(id: number, status: string) {
      return apiRequest<SeoOpportunityTaskItem>(
        `/admin/seo/opportunity-tasks/${id}/`,
        { method: "PATCH", auth: true, body: { status } },
      );
    },
  },

  growthTasks: {
    list() {
      return apiRequest<GrowthTaskItem[]>("/admin/growth-agent/tasks/", {
        auth: true,
      });
    },
    accept(id: number) {
      return apiRequest<GrowthTaskItem>(
        `/admin/growth-agent/tasks/${id}/accept/`,
        { method: "POST", auth: true, body: {} },
      );
    },
    complete(id: number) {
      return apiRequest<GrowthTaskItem>(
        `/admin/growth-agent/tasks/${id}/complete/`,
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  launchReadiness: {
    get() {
      return apiRequest<ReadinessCheckItem[] | { checks: ReadinessCheckItem[] }>(
        "/admin/launch-readiness/",
        { auth: true },
      );
    },
    run() {
      return apiRequest<ReadinessCheckItem[] | { checks: ReadinessCheckItem[] }>(
        "/admin/launch-readiness/",
        { method: "POST", auth: true, body: {} },
      );
    },
  },

  salesLeads: {
    create(input: {
      name: string;
      email: string;
      company?: string;
      role?: string;
      message?: string;
      intent?: string;
    }) {
      return apiRequest<SalesLeadItem>("/marketplace/leads/", {
        method: "POST",
        body: input,
      });
    },
    adminList() {
      return apiRequest<SalesLeadItem[]>("/admin/marketplace/leads/", {
        auth: true,
      });
    },
  },

  referrals: {
    me() {
      return apiRequest<ReferralMeData>("/referrals/me/", { auth: true });
    },
    claim(code: string) {
      return apiRequest<Record<string, unknown>>("/referrals/claim/", {
        method: "POST",
        auth: true,
        body: { code },
      });
    },
    resolve(code: string) {
      return apiRequest<{ code: string; valid?: boolean }>(
        `/referrals/r/${encodeURIComponent(code)}/`,
      );
    },
    adminStats() {
      return apiRequest<Record<string, unknown>>("/admin/referrals/stats/", {
        auth: true,
      });
    },
  },

  gamification: {
    me() {
      return apiRequest<GamificationMeData>("/gamification/me/", { auth: true });
    },
    badges() {
      return apiRequest<BadgeItem[]>("/gamification/badges/");
    },
  },
};

export { setTokens, clearTokens, getRefreshToken };
