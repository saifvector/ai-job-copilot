'use client';

import React, { useEffect, useState } from 'react';
import { useDeveloperStore } from '@/store/developer-store';
import { useWebhookStore } from '@/store/webhook-store';
import { useIntegrationStore } from '@/store/integration-store';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';
import {
  Key,
  Webhook as WebhookIcon,
  Layers,
  Cpu,
  BarChart3,
  Code2,
  Copy,
  Check,
  RefreshCw,
  Trash2,
  Plus,
  ExternalLink,
  Shield,
  Activity,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Send,
  Terminal,
  FileText,
  Mail,
  Calendar,
  Cloud,
  Share2,
} from 'lucide-react';

const AVAILABLE_SCOPES = [
  { id: 'read:profile', label: 'Read Profile', desc: 'Candidate biographical data and preferences' },
  { id: 'read:resume', label: 'Read Resumes', desc: 'Parsed resumes, skills, and work history' },
  { id: 'read:matches', label: 'Read Matches', desc: 'AI job match scores, strengths, and recommendations' },
  { id: 'read:applications', label: 'Read Applications', desc: 'Job application pipeline statuses and records' },
  { id: 'write:applications', label: 'Write Applications', desc: 'Submit and track job applications programmatically' },
  { id: 'read:reports', label: 'Read Reports', desc: 'Exported analysis documents and career metrics' },
];

const WEBHOOK_EVENTS = [
  { id: 'resume.parsed', label: 'Resume Parsed', desc: 'Fires when a new resume is analyzed and indexed' },
  { id: 'job.matched', label: 'Job Matched', desc: 'Fires when an AI match score exceeds threshold' },
  { id: 'report.generated', label: 'Report Generated', desc: 'Fires when PDF/JSON analytics report completes' },
  { id: 'application.created', label: 'Application Created', desc: 'Fires when a candidate submits an application' },
  { id: 'application.updated', label: 'Application Updated', desc: 'Fires on application status or interview stage update' },
];

export default function DeveloperPortalPage() {
  const [activeTab, setActiveTab] = useState<'keys' | 'webhooks' | 'integrations' | 'plugins' | 'analytics' | 'explorer'>('keys');

  // Stores
  const {
    apiKeys,
    newKeySecret,
    analytics,
    plugins,
    lastHookResult,
    loading: keysLoading,
    error: keysError,
    fetchApiKeys,
    createApiKey,
    rotateApiKey,
    revokeApiKey,
    dismissNewKeySecret,
    fetchAnalytics,
    fetchPlugins,
    registerPlugin,
    executePluginHook,
  } = useDeveloperStore();

  const {
    webhooks,
    selectedWebhookId,
    deliveries,
    testResult,
    loading: webhooksLoading,
    testing: webhooksTesting,
    error: webhooksError,
    fetchWebhooks,
    createWebhook,
    deleteWebhook,
    testWebhook,
    selectWebhook,
    clearTestResult,
  } = useWebhookStore();

  const {
    integrations,
    syncingProvider,
    syncResult,
    error: integrationsError,
    fetchIntegrations,
    connectIntegration,
    disconnectIntegration,
    syncIntegration,
    clearSyncResult,
  } = useIntegrationStore();

  // Local state for modals & forms
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [isCreateKeyOpen, setIsCreateKeyOpen] = useState(false);
  const [keyName, setKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>([
    'read:profile',
    'read:resume',
    'read:matches',
    'read:applications',
    'write:applications',
    'read:reports',
  ]);
  const [rateLimit, setRateLimit] = useState('60');

  const [isCreateWebhookOpen, setIsCreateWebhookOpen] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([
    'job.matched',
    'application.created',
  ]);

  const [isDeliveriesModalOpen, setIsDeliveriesModalOpen] = useState(false);
  const [isHookExecutionModalOpen, setIsHookExecutionModalOpen] = useState(false);
  const [executingPluginId, setExecutingPluginId] = useState<string>('');
  const [executingHookName, setExecutingHookName] = useState<string>('');
  const [hookPayloadStr, setHookPayloadStr] = useState<string>('{}');

  useEffect(() => {
    fetchApiKeys();
    fetchWebhooks();
    fetchIntegrations();
    fetchPlugins();
    fetchAnalytics(7);
  }, []);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(id);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  const handleCreateApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyName.trim()) return;
    const res = await createApiKey({
      name: keyName.trim(),
      scopes: selectedScopes,
      rate_limit: parseInt(rateLimit, 10) || 60,
    });
    if (res) {
      setKeyName('');
      setIsCreateKeyOpen(false);
    }
  };

  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!webhookUrl.trim()) return;
    const res = await createWebhook({
      endpoint: webhookUrl.trim(),
      events: selectedEvents,
    });
    if (res) {
      setWebhookUrl('');
      setIsCreateWebhookOpen(false);
    }
  };

  const handleOpenDeliveries = (webhookId: string) => {
    selectWebhook(webhookId);
    setIsDeliveriesModalOpen(true);
  };

  const handleOpenHookExec = (pluginId: string, hookName: string) => {
    setExecutingPluginId(pluginId);
    setExecutingHookName(hookName);
    setHookPayloadStr(
      hookName === 'on_custom_export'
        ? JSON.stringify({ title: 'Staff SRE Resume', format: 'pdf', pages: 2 }, null, 2)
        : JSON.stringify({ query: 'Backend', location: 'Remote' }, null, 2)
    );
    setIsHookExecutionModalOpen(true);
  };

  const handleExecuteHook = async () => {
    try {
      const payload = JSON.parse(hookPayloadStr || '{}');
      await executePluginHook(executingPluginId, executingHookName, payload);
    } catch {
      alert('Invalid JSON payload');
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground pb-16">
      {/* Header */}
      <div className="border-b border-border/60 bg-card/40 backdrop-blur-md px-6 py-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                <Code2 className="h-5 w-5" />
              </div>
              <h1 className="text-3xl font-bold tracking-tight">Developer Portal</h1>
              <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                v1.0 Live API
              </Badge>
            </div>
            <p className="text-muted-foreground text-sm max-w-2xl">
              Build third-party integrations, ingest events via HMAC-signed webhooks, deploy modular plugins,
              and query candidate analytics via our versioned Public API.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg border border-border text-sm font-medium hover:bg-muted/50 transition-colors"
            >
              <Terminal className="h-4 w-4 text-primary" />
              OpenAPI Swagger
              <ExternalLink className="h-3 w-3 text-muted-foreground" />
            </a>
            <Button
              onClick={() => setIsCreateKeyOpen(true)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Create API Key
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto flex items-center gap-2 mt-8 border-b border-border/40 overflow-x-auto">
          {[
            { id: 'keys', label: 'API Keys', icon: Key, count: apiKeys.length },
            { id: 'webhooks', label: 'Webhooks', icon: WebhookIcon, count: webhooks.length },
            { id: 'integrations', label: 'Integrations', icon: Layers, count: integrations.filter((i) => i.connected).length },
            { id: 'plugins', label: 'Plugin SDK', icon: Cpu, count: plugins.length },
            { id: 'analytics', label: 'API Telemetry', icon: BarChart3 },
            { id: 'explorer', label: 'API Explorer', icon: Terminal },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'keys' | 'webhooks' | 'integrations' | 'plugins' | 'analytics' | 'explorer')}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'border-primary text-primary bg-primary/5'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/30'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {tab.count !== undefined && (
                  <span className={`text-xs px-2 py-0.5 rounded-full ${isActive ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'}`}>
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Error Alert Banner */}
        {(keysError || webhooksError || integrationsError) && (
          <div className="mb-6 p-4 rounded-xl border border-destructive/40 bg-destructive/10 text-destructive flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 flex-shrink-0" />
              <p className="text-sm font-medium">{keysError || webhooksError || integrationsError}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                useDeveloperStore.getState().clearError();
                useWebhookStore.getState().clearError();
                useIntegrationStore.getState().clearError();
              }}
            >
              Dismiss
            </Button>
          </div>
        )}

        {/* New API Key Secret Alert Modal */}
        {newKeySecret && (
          <div className="mb-8 p-6 rounded-2xl border-2 border-emerald-500/40 bg-emerald-950/20 backdrop-blur-md shadow-2xl relative">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <Shield className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-emerald-300">API Key Generated Successfully</h3>
                  <p className="text-xs text-muted-foreground">
                    Please copy your secret key now. For your security, this key will never be shown again!
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={dismissNewKeySecret} className="text-muted-foreground hover:text-foreground">
                Done
              </Button>
            </div>

            <div className="mt-4 flex items-center gap-3 p-3.5 bg-black/60 rounded-xl border border-border/80 font-mono text-sm">
              <span className="text-emerald-400 font-medium select-all flex-1 truncate">{newKeySecret.secret_key}</span>
              <Button
                size="sm"
                onClick={() => handleCopy(newKeySecret.secret_key, 'new-secret')}
                className="bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1.5"
              >
                {copiedKey === 'new-secret' ? (
                  <>
                    <Check className="h-4 w-4" /> Copied!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" /> Copy Secret
                  </>
                )}
              </Button>
            </div>

            <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">Header Usage:</span>
              <code className="bg-muted px-2 py-0.5 rounded text-primary">X-API-Key: {newKeySecret.prefix}...</code>
            </div>
          </div>
        )}

        {/* TAB 1: API KEYS */}
        {activeTab === 'keys' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Active API Credentials</h2>
                <p className="text-sm text-muted-foreground">Authenticate automated systems against /api/public/v1/*</p>
              </div>
              <Button onClick={() => setIsCreateKeyOpen(true)} className="flex items-center gap-2">
                <Plus className="h-4 w-4" /> Generate New Key
              </Button>
            </div>

            {apiKeys.length === 0 ? (
              <Card className="border-border/60 bg-card/40 text-center py-12">
                <CardContent className="space-y-4">
                  <div className="h-12 w-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto text-primary">
                    <Key className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">No API Keys Generated</h3>
                    <p className="text-sm text-muted-foreground">Create your first API key to start calling the public API programmatically.</p>
                  </div>
                  <Button onClick={() => setIsCreateKeyOpen(true)}>Create Key</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {apiKeys.map((key) => (
                  <Card key={key.id} className="border-border/60 bg-card/30 backdrop-blur-sm hover:border-primary/40 transition-all">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <span className="font-semibold text-lg">{key.name}</span>
                            <Badge variant="outline" className="font-mono text-xs bg-muted/60">
                              {key.prefix}...
                            </Badge>
                            {key.is_active ? (
                              <Badge className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Active</Badge>
                            ) : (
                              <Badge variant="destructive">Revoked</Badge>
                            )}
                          </div>

                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {key.scopes.map((scope) => (
                              <span key={scope} className="text-xs px-2 py-0.5 rounded-md bg-primary/10 text-primary border border-primary/20">
                                {scope}
                              </span>
                            ))}
                          </div>

                          <div className="flex items-center gap-6 text-xs text-muted-foreground pt-2">
                            <span className="flex items-center gap-1.5">
                              <Activity className="h-3.5 w-3.5 text-primary" />
                              {key.usage_count.toLocaleString()} calls this month (limit: {key.monthly_limit.toLocaleString()})
                            </span>
                            <span className="flex items-center gap-1.5">
                              <Clock className="h-3.5 w-3.5" />
                              {key.rate_limit} req/min
                            </span>
                            {key.last_used_at && (
                              <span>Last active: {new Date(key.last_used_at).toLocaleDateString()}</span>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => rotateApiKey(key.id)}
                            className="flex items-center gap-1.5 hover:border-amber-500/50 hover:text-amber-400"
                          >
                            <RefreshCw className="h-3.5 w-3.5" /> Rotate
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              if (confirm(`Revoke API key "${key.name}"? Active integrations using this key will immediately lose access.`)) {
                                revokeApiKey(key.id);
                              }
                            }}
                            className="text-destructive hover:bg-destructive/10"
                          >
                            <Trash2 className="h-3.5 w-3.5" /> Revoke
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: WEBHOOKS */}
        {activeTab === 'webhooks' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Outbound Webhooks</h2>
                <p className="text-sm text-muted-foreground">Receive real-time HTTP POST events with HMAC-SHA256 signatures</p>
              </div>
              <Button onClick={() => setIsCreateWebhookOpen(true)} className="flex items-center gap-2">
                <Plus className="h-4 w-4" /> Add Webhook Endpoint
              </Button>
            </div>

            {/* Test Result Banner */}
            {testResult && (
              <div className={`p-4 rounded-xl border flex items-center justify-between ${testResult.success ? 'bg-emerald-950/20 border-emerald-500/40' : 'bg-rose-950/20 border-rose-500/40'}`}>
                <div className="flex items-center gap-3">
                  {testResult.success ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <XCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />
                  )}
                  <div>
                    <p className="text-sm font-semibold">
                      {testResult.success ? 'Test Delivery Succeeded' : 'Test Delivery Failed'} (HTTP {testResult.status_code || 'Err'}) in {testResult.duration_ms}ms
                    </p>
                    <p className="text-xs text-muted-foreground font-mono truncate max-w-xl">
                      Signature: {testResult.signature}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={clearTestResult}>
                  Dismiss
                </Button>
              </div>
            )}

            {webhooks.length === 0 ? (
              <Card className="border-border/60 bg-card/40 text-center py-12">
                <CardContent className="space-y-4">
                  <div className="h-12 w-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto text-primary">
                    <WebhookIcon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">No Webhooks Configured</h3>
                    <p className="text-sm text-muted-foreground">Subscribe to real-time events like application status updates and AI match alerts.</p>
                  </div>
                  <Button onClick={() => setIsCreateWebhookOpen(true)}>Add Endpoint</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {webhooks.map((wh) => (
                  <Card key={wh.id} className="border-border/60 bg-card/30 backdrop-blur-sm">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <span className="font-mono text-sm font-semibold">{wh.endpoint}</span>
                            {wh.enabled ? (
                              <Badge className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Active</Badge>
                            ) : (
                              <Badge variant="outline" className="text-muted-foreground">Disabled</Badge>
                            )}
                            <Badge variant="outline" className="font-mono text-xs text-muted-foreground">
                              {wh.secret_preview}...
                            </Badge>
                          </div>

                          <div className="flex flex-wrap gap-1.5">
                            {wh.events.map((evt) => (
                              <span key={evt} className="text-xs px-2 py-0.5 rounded-md bg-secondary text-secondary-foreground border border-border">
                                {evt}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={webhooksTesting}
                            onClick={() => testWebhook(wh.id)}
                            className="flex items-center gap-1.5"
                          >
                            <Send className="h-3.5 w-3.5" /> Test Ping
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleOpenDeliveries(wh.id)}
                            className="flex items-center gap-1.5"
                          >
                            <FileText className="h-3.5 w-3.5" /> Delivery Logs
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              if (confirm('Delete this webhook subscription?')) deleteWebhook(wh.id);
                            }}
                            className="text-destructive hover:bg-destructive/10"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: INTEGRATIONS */}
        {activeTab === 'integrations' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Third-Party Ecosystem</h2>
                <p className="text-sm text-muted-foreground">Connect external email, calendar, cloud storage, and team messaging providers</p>
              </div>
              <Button variant="outline" onClick={() => fetchIntegrations()} className="flex items-center gap-2">
                <RefreshCw className="h-4 w-4" /> Refresh Statuses
              </Button>
            </div>

            {/* Sync Result Toast */}
            {syncResult && (
              <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/20 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  <div>
                    <p className="text-sm font-semibold capitalize">
                      {syncResult.provider} Sync Completed: {syncResult.synced_items_count} items processed
                    </p>
                    <p className="text-xs text-muted-foreground font-mono">
                      {JSON.stringify(syncResult.details)}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={clearSyncResult}>
                  Dismiss
                </Button>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {integrations.map((item) => {
                const getProviderIcon = () => {
                  switch (item.provider) {
                    case 'gmail':
                    case 'outlook':
                      return <Mail className="h-5 w-5 text-blue-400" />;
                    case 'google_calendar':
                    case 'outlook_calendar':
                      return <Calendar className="h-5 w-5 text-emerald-400" />;
                    case 'google_drive':
                    case 'dropbox':
                    case 'onedrive':
                      return <Cloud className="h-5 w-5 text-amber-400" />;
                    case 'slack':
                      return <Share2 className="h-5 w-5 text-purple-400" />;
                    default:
                      return <Layers className="h-5 w-5 text-primary" />;
                  }
                };

                return (
                  <Card key={item.provider} className="border-border/60 bg-card/30 backdrop-blur-sm flex flex-col justify-between">
                    <CardContent className="p-6 space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="h-10 w-10 rounded-xl bg-muted/60 border border-border flex items-center justify-center">
                          {getProviderIcon()}
                        </div>
                        {item.connected ? (
                          <Badge className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Connected</Badge>
                        ) : (
                          <Badge variant="outline" className="text-muted-foreground">Disconnected</Badge>
                        )}
                      </div>

                      <div>
                        <h3 className="font-semibold text-lg">{item.display_name}</h3>
                        <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                      </div>

                      <div className="text-xs text-muted-foreground border-t border-border/40 pt-3">
                        <span className="font-medium text-foreground">Category:</span> <span className="capitalize">{item.category}</span>
                        {item.last_sync_at && (
                          <div className="mt-1">
                            <span className="font-medium text-foreground">Last Sync:</span>{' '}
                            {new Date(item.last_sync_at).toLocaleString()}
                          </div>
                        )}
                      </div>

                      <div className="pt-2 flex items-center gap-2">
                        {item.connected ? (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={syncingProvider === item.provider}
                              onClick={() => syncIntegration(item.provider)}
                              className="flex-1 flex items-center justify-center gap-1.5"
                            >
                              <RefreshCw className={`h-3.5 w-3.5 ${syncingProvider === item.provider ? 'animate-spin' : ''}`} />
                              {syncingProvider === item.provider ? 'Syncing...' : 'Sync Now'}
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => disconnectIntegration(item.provider)}
                              className="text-destructive hover:bg-destructive/10"
                            >
                              Disconnect
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => connectIntegration(item.provider)}
                            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
                          >
                            Connect Account
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 4: PLUGIN SDK */}
        {activeTab === 'plugins' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Modular Plugin SDK</h2>
                <p className="text-sm text-muted-foreground">Register custom job providers, exporters, and analytical telemetry handlers</p>
              </div>
            </div>

            {/* Last Execution Result */}
            {lastHookResult && (
              <div className="p-4 rounded-xl border border-border/80 bg-card/60 backdrop-blur-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Terminal className="h-4 w-4 text-primary" />
                    <span className="text-sm font-semibold">Execution Output ({lastHookResult.plugin_id}::{lastHookResult.hook})</span>
                  </div>
                  <Badge variant={lastHookResult.success ? 'default' : 'destructive'}>
                    {lastHookResult.success ? 'Success' : 'Failed'}
                  </Badge>
                </div>
                <pre className="p-3 bg-black/50 rounded-lg text-xs font-mono overflow-x-auto text-emerald-400">
                  {JSON.stringify(lastHookResult.result, null, 2)}
                </pre>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {plugins.map((plugin) => (
                <Card key={plugin.id} className="border-border/60 bg-card/30 backdrop-blur-sm flex flex-col justify-between">
                  <CardContent className="p-6 space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                        <Cpu className="h-5 w-5" />
                      </div>
                      <Badge variant="outline" className="font-mono text-xs">
                        v{plugin.version}
                      </Badge>
                    </div>

                    <div>
                      <h3 className="font-semibold text-lg">{plugin.name}</h3>
                      <p className="text-xs text-muted-foreground mt-1">{plugin.description}</p>
                    </div>

                    <div className="space-y-1.5 border-t border-border/40 pt-3">
                      <span className="text-xs font-semibold text-foreground">Declared Hooks:</span>
                      <div className="flex flex-wrap gap-1">
                        {plugin.hooks.map((hook) => (
                          <span key={hook} className="text-xs px-2 py-0.5 rounded bg-muted font-mono text-muted-foreground">
                            {hook}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="pt-2">
                      {plugin.hooks.map((hook) => (
                        <Button
                          key={hook}
                          size="sm"
                          variant="outline"
                          onClick={() => handleOpenHookExec(plugin.id, hook)}
                          className="w-full mt-2 flex items-center justify-center gap-1.5 text-xs"
                        >
                          <Terminal className="h-3.5 w-3.5" /> Run Hook: {hook}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: API TELEMETRY */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">API Usage & Telemetry</h2>
                <p className="text-sm text-muted-foreground">Real-time metrics, error rate tracking, and p95 latency percentiles</p>
              </div>
              <div className="flex items-center gap-2">
                {[1, 7, 30].map((days) => (
                  <Button
                    key={days}
                    variant={analytics?.period_days === days ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => fetchAnalytics(days)}
                  >
                    {days === 1 ? 'Last 24h' : `Last ${days}d`}
                  </Button>
                ))}
              </div>
            </div>

            {/* Metrics Overview Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="border-border/60 bg-card/40">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between text-muted-foreground text-xs font-medium">
                    <span>Total Requests</span>
                    <Activity className="h-4 w-4 text-primary" />
                  </div>
                  <div className="text-3xl font-bold mt-2">
                    {analytics?.total_requests.toLocaleString() || 0}
                  </div>
                  <span className="text-xs text-muted-foreground mt-1 block">In selected period</span>
                </CardContent>
              </Card>

              <Card className="border-border/60 bg-card/40">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between text-muted-foreground text-xs font-medium">
                    <span>Failed Requests</span>
                    <XCircle className="h-4 w-4 text-rose-400" />
                  </div>
                  <div className="text-3xl font-bold mt-2 text-rose-400">
                    {analytics?.total_errors.toLocaleString() || 0}
                  </div>
                  <span className="text-xs text-muted-foreground mt-1 block">HTTP 4xx / 5xx errors</span>
                </CardContent>
              </Card>

              <Card className="border-border/60 bg-card/40">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between text-muted-foreground text-xs font-medium">
                    <span>Error Rate</span>
                    <BarChart3 className="h-4 w-4 text-amber-400" />
                  </div>
                  <div className="text-3xl font-bold mt-2">
                    {analytics?.error_rate.toFixed(2) || '0.00'}%
                  </div>
                  <span className="text-xs text-muted-foreground mt-1 block">Reliability SLA: 99.9%</span>
                </CardContent>
              </Card>

              <Card className="border-border/60 bg-card/40">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between text-muted-foreground text-xs font-medium">
                    <span>P95 Latency</span>
                    <Clock className="h-4 w-4 text-emerald-400" />
                  </div>
                  <div className="text-3xl font-bold mt-2 text-emerald-400">
                    {analytics?.p95_latency_ms.toFixed(1) || '0.0'}ms
                  </div>
                  <span className="text-xs text-muted-foreground mt-1 block">Sub-100ms standard</span>
                </CardContent>
              </Card>
            </div>

            {/* Endpoint Breakdown */}
            <Card className="border-border/60 bg-card/30">
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-4">Traffic Breakdown by Endpoint</h3>
                {analytics?.endpoint_breakdown.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-6 text-center">No API calls recorded in this timeframe.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="border-b border-border/60 text-xs text-muted-foreground uppercase">
                        <tr>
                          <th className="pb-3 font-semibold">Method</th>
                          <th className="pb-3 font-semibold">Endpoint Path</th>
                          <th className="pb-3 font-semibold text-right">Requests</th>
                          <th className="pb-3 font-semibold text-right">Errors</th>
                          <th className="pb-3 font-semibold text-right">Avg Latency</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40 font-mono text-xs">
                        {analytics?.endpoint_breakdown.map((row, idx) => (
                          <tr key={idx} className="hover:bg-muted/30">
                            <td className="py-3">
                              <Badge variant="outline" className={row.method === 'GET' ? 'text-blue-400' : 'text-emerald-400'}>
                                {row.method}
                              </Badge>
                            </td>
                            <td className="py-3 text-foreground font-medium">{row.endpoint}</td>
                            <td className="py-3 text-right text-foreground font-semibold">{row.count.toLocaleString()}</td>
                            <td className="py-3 text-right text-rose-400">{row.error_count}</td>
                            <td className="py-3 text-right text-emerald-400">{row.avg_latency_ms.toFixed(1)}ms</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* TAB 6: API EXPLORER */}
        {activeTab === 'explorer' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold">Public API Reference & Code Samples</h2>
              <p className="text-sm text-muted-foreground">Explore interactive code samples for all /api/public/v1 endpoints</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[
                {
                  title: 'Get Candidate Profile',
                  endpoint: 'GET /api/public/v1/profile',
                  curl: `curl -X GET "http://localhost:8000/api/public/v1/profile" \\\n  -H "X-API-Key: ajc_live_your_api_key_here"`,
                  ts: `import { JobCopilotClient } from '@jobcopilot/sdk';\n\nconst client = new JobCopilotClient({ apiKey: 'ajc_live_...' });\nconst profile = await client.profile.get();\nconsole.log(profile.name, profile.preferred_roles);`,
                },
                {
                  title: 'Query AI Match Results',
                  endpoint: 'GET /api/public/v1/matches?min_score=80',
                  curl: `curl -X GET "http://localhost:8000/api/public/v1/matches?min_score=80" \\\n  -H "X-API-Key: ajc_live_your_api_key_here"`,
                  ts: `const matches = await client.matches.list({ minScore: 80 });\nfor (const match of matches.items) {\n  console.log(\`\${match.job_title} at \${match.company}: \${match.overall_score}%\`);\n}`,
                },
                {
                  title: 'Create Application Record',
                  endpoint: 'POST /api/public/v1/applications',
                  curl: `curl -X POST "http://localhost:8000/api/public/v1/applications" \\\n  -H "X-API-Key: ajc_live_your_api_key_here" \\\n  -H "Content-Type: application/json" \\\n  -d '{"job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "status": "Applied"}'`,
                  ts: `const app = await client.applications.create({\n  jobId: '3fa85f64-...',\n  status: 'Applied',\n  notes: 'Referred by tech lead',\n});`,
                },
                {
                  title: 'List Parsed Resumes',
                  endpoint: 'GET /api/public/v1/resumes',
                  curl: `curl -X GET "http://localhost:8000/api/public/v1/resumes" \\\n  -H "X-API-Key: ajc_live_your_api_key_here"`,
                  ts: `const resumes = await client.resumes.list();\nconsole.log(\`Candidate has \${resumes.total} indexed resumes\`);`,
                },
              ].map((route, i) => (
                <Card key={i} className="border-border/60 bg-card/30">
                  <CardContent className="p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-base">{route.title}</h3>
                      <Badge variant="outline" className="font-mono text-xs text-primary">
                        {route.endpoint}
                      </Badge>
                    </div>

                    <div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-1.5">
                        <span>cURL Command</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopy(route.curl, `curl-${i}`)}
                          className="h-6 px-2 text-xs"
                        >
                          {copiedKey === `curl-${i}` ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                        </Button>
                      </div>
                      <pre className="p-3 bg-black/60 rounded-xl font-mono text-xs text-muted-foreground overflow-x-auto">
                        {route.curl}
                      </pre>
                    </div>

                    <div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-1.5">
                        <span>TypeScript SDK</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopy(route.ts, `ts-${i}`)}
                          className="h-6 px-2 text-xs"
                        >
                          {copiedKey === `ts-${i}` ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                        </Button>
                      </div>
                      <pre className="p-3 bg-black/60 rounded-xl font-mono text-xs text-emerald-400/90 overflow-x-auto">
                        {route.ts}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* MODAL: CREATE API KEY */}
      <Modal isOpen={isCreateKeyOpen} onClose={() => setIsCreateKeyOpen(false)} title="Generate New API Key">
        <form onSubmit={handleCreateApiKey} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Key Label / Name</label>
            <Input
              required
              placeholder="e.g. Production ATS Sync, Zapier Integration"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Rate Limit (Requests / Minute)</label>
            <Input
              type="number"
              min="1"
              max="1000"
              value={rateLimit}
              onChange={(e) => setRateLimit(e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Permissions & Scopes</label>
            <div className="mt-2 space-y-2 max-h-48 overflow-y-auto border border-border/60 rounded-xl p-3 bg-muted/20">
              {AVAILABLE_SCOPES.map((scope) => (
                <label key={scope.id} className="flex items-start gap-2.5 text-xs cursor-pointer hover:bg-muted/40 p-1.5 rounded-lg">
                  <input
                    type="checkbox"
                    checked={selectedScopes.includes(scope.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedScopes([...selectedScopes, scope.id]);
                      } else {
                        setSelectedScopes(selectedScopes.filter((s) => s !== scope.id));
                      }
                    }}
                    className="mt-0.5 rounded border-border"
                  />
                  <div>
                    <span className="font-semibold text-foreground">{scope.label}</span>{' '}
                    <code className="text-primary font-mono text-[10px]">({scope.id})</code>
                    <p className="text-muted-foreground">{scope.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsCreateKeyOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={keysLoading || !keyName.trim()}>
              Generate Key
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: CREATE WEBHOOK */}
      <Modal isOpen={isCreateWebhookOpen} onClose={() => setIsCreateWebhookOpen(false)} title="Register Webhook Endpoint">
        <form onSubmit={handleCreateWebhook} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Endpoint URL (HTTPS)</label>
            <Input
              required
              type="url"
              placeholder="https://api.yourdomain.com/webhooks/job-copilot"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              className="mt-1 font-mono text-xs"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Event Subscriptions</label>
            <div className="mt-2 space-y-2 border border-border/60 rounded-xl p-3 bg-muted/20">
              {WEBHOOK_EVENTS.map((evt) => (
                <label key={evt.id} className="flex items-start gap-2.5 text-xs cursor-pointer hover:bg-muted/40 p-1.5 rounded-lg">
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes(evt.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedEvents([...selectedEvents, evt.id]);
                      } else {
                        setSelectedEvents(selectedEvents.filter((s) => s !== evt.id));
                      }
                    }}
                    className="mt-0.5 rounded border-border"
                  />
                  <div>
                    <span className="font-semibold text-foreground">{evt.label}</span>{' '}
                    <code className="text-primary font-mono text-[10px]">({evt.id})</code>
                    <p className="text-muted-foreground">{evt.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsCreateWebhookOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={webhooksLoading || !webhookUrl.trim() || selectedEvents.length === 0}>
              Subscribe
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: WEBHOOK DELIVERIES */}
      <Modal
        isOpen={isDeliveriesModalOpen}
        onClose={() => setIsDeliveriesModalOpen(false)}
        title="Webhook Delivery History"
      >
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {deliveries.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">No delivery attempts recorded yet.</p>
          ) : (
            <div className="space-y-2">
              {deliveries.map((d) => (
                <div key={d.id} className="p-3 bg-muted/30 rounded-xl border border-border/60 text-xs font-mono space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground">{d.event}</span>
                    <Badge variant={d.success ? 'default' : 'destructive'} className="text-[10px]">
                      {d.status_code ? `HTTP ${d.status_code}` : 'Failed'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-muted-foreground text-[11px]">
                    <span>{d.duration_ms}ms latency</span>
                    <span>{new Date(d.created_at).toLocaleTimeString()}</span>
                  </div>
                  {d.error_message && (
                    <div className="text-rose-400 text-[11px] truncate pt-1">{d.error_message}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </Modal>

      {/* MODAL: RUN PLUGIN HOOK */}
      <Modal
        isOpen={isHookExecutionModalOpen}
        onClose={() => setIsHookExecutionModalOpen(false)}
        title={`Execute Hook: ${executingPluginId}::${executingHookName}`}
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Input Payload (JSON)</label>
            <textarea
              rows={6}
              value={hookPayloadStr}
              onChange={(e) => setHookPayloadStr(e.target.value)}
              className="mt-1 w-full rounded-xl bg-black/60 border border-border p-3 font-mono text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setIsHookExecutionModalOpen(false)}>
              Close
            </Button>
            <Button
              onClick={() => {
                handleExecuteHook();
                setIsHookExecutionModalOpen(false);
              }}
            >
              Execute
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
