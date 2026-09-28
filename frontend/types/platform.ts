export interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  scopes: string[];
  rate_limit: number;
  monthly_limit: number;
  usage_count: number;
  is_active: boolean;
  expires_at: string | null;
  last_used_at: string | null;
  created_at: string;
}

export interface ApiKeyCreated extends ApiKey {
  secret_key: string;
}

export interface ApiKeyCreatePayload {
  name: string;
  scopes?: string[];
  rate_limit?: number;
  monthly_limit?: number;
  expires_in_days?: number;
}

export interface ApiKeyRotatePayload {
  expires_in_days?: number;
}

export interface Webhook {
  id: string;
  endpoint: string;
  events: string[];
  enabled: boolean;
  secret_preview: string;
  secret?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface WebhookCreatePayload {
  endpoint: string;
  events?: string[];
  description?: string;
}

export interface WebhookUpdatePayload {
  endpoint?: string;
  events?: string[];
  enabled?: boolean;
  description?: string;
}

export interface WebhookDeliveryLog {
  id: string;
  webhook_id: string;
  event: string;
  status_code: number | null;
  duration_ms: number;
  success: boolean;
  error_message: string | null;
  created_at: string;
}

export interface WebhookTestResult {
  success: boolean;
  status_code: number | null;
  duration_ms: number;
  error: string | null;
  signature: string;
}

export interface OAuthConnection {
  id: string;
  user_id: string;
  provider: string;
  provider_user_id: string | null;
  scopes: string[];
  status: 'connected' | 'disconnected' | 'error';
  metadata: Record<string, any> | null;
  last_sync_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IntegrationStatus {
  provider: string;
  category: 'email' | 'calendar' | 'storage' | 'notification';
  display_name: string;
  description: string;
  connected: boolean;
  status: string;
  scopes: string[];
  last_sync_at: string | null;
}

export interface OAuthConnectPayload {
  auth_code?: string;
  scopes?: string[];
  metadata?: Record<string, any>;
}

export interface OAuthSyncResult {
  provider: string;
  status: string;
  synced_items_count: number;
  details: Record<string, any>;
}

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  hooks: string[];
  enabled: boolean;
  settings_schema?: Record<string, any>;
}

export interface PluginRegisterPayload {
  id: string;
  name: string;
  version: string;
  description?: string;
  author?: string;
  hooks?: string[];
}

export interface PluginExecutionResult {
  plugin_id: string;
  hook: string;
  success: boolean;
  result: any;
  error?: string;
}

export interface EndpointUsageItem {
  endpoint: string;
  method: string;
  count: number;
  error_count: number;
  avg_latency_ms: number;
}

export interface ApiAnalyticsSummary {
  period_days: number;
  total_requests: number;
  total_errors: number;
  error_rate: number;
  p95_latency_ms: number;
  endpoint_breakdown: EndpointUsageItem[];
}
