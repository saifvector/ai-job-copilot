'use client';

import * as React from 'react';
import {
  Cpu,
  Bot,
  Play,
  RotateCcw,
  XCircle,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  Layers,
  Activity,
  Zap,
  Shield,
  Sliders,
  Send,
  RefreshCw,
  Search,
  Filter,
  Eye,
  BrainCircuit,
  Workflow,
  Check,
  AlertCircle,
  Database,
  Terminal,
} from 'lucide-react';
import { useAgentStore, useWorkflowStore, useTaskStore } from '@/store';
import { AgentInfo, AgentTask, WorkflowExecution, WorkflowTemplate } from '@/types';

export default function AgentsPage() {
  const {
    agents,
    selectedAgent,
    memories,
    routeRecommendation,
    loading: agentsLoading,
    executing: agentExecuting,
    lastExecutionResult,
    fetchAgents,
    selectAgent,
    executeAgent,
    fetchMemories,
    evaluateModelRoute,
  } = useAgentStore();

  const {
    templates,
    executions,
    selectedExecution,
    selectedTemplate,
    metrics,
    loading: workflowLoading,
    executing: workflowExecuting,
    fetchTemplates,
    fetchExecutions,
    fetchExecutionDetail,
    executeWorkflow,
    fetchMetrics,
    selectTemplate,
    selectExecution,
  } = useWorkflowStore();

  const {
    tasks,
    selectedTask,
    filterStatus,
    filterAgent,
    loading: tasksLoading,
    actionLoading,
    fetchTasks,
    retryTask,
    cancelTask,
    selectTask,
    setFilterStatus,
    setFilterAgent,
  } = useTaskStore();

  const [activeTab, setActiveTab] = React.useState<'agents' | 'workflows' | 'tasks' | 'router'>('agents');

  // Agent execution modal state
  const [isExecModalOpen, setIsExecModalOpen] = React.useState(false);
  const [execPayload, setExecPayload] = React.useState('{\n  "mode": "analyze",\n  "target_role": "Staff Software Engineer",\n  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"]\n}');
  const [execModelOverride, setExecModelOverride] = React.useState('');

  // Workflow trigger state
  const [wfContext, setWfContext] = React.useState('{\n  "candidate_target_role": "Lead Distributed Systems Engineer",\n  "resume_skills": ["Python", "FastAPI", "PostgreSQL", "Kafka", "Kubernetes"]\n}');

  // Model router simulation state
  const [routerTaskType, setRouterTaskType] = React.useState('resume_scoring');
  const [routerComplexity, setRouterComplexity] = React.useState('MEDIUM');
  const [routerSpeed, setRouterSpeed] = React.useState('BALANCED');
  const [routerCost, setRouterCost] = React.useState('STANDARD');
  const [routerPrivacy, setRouterPrivacy] = React.useState('CLOUD');

  // Task details modal
  const [inspectTask, setInspectTask] = React.useState<AgentTask | null>(null);

  React.useEffect(() => {
    fetchAgents();
    fetchTemplates();
    fetchExecutions();
    fetchTasks();
    fetchMetrics();
    fetchMemories();
  }, [fetchAgents, fetchTemplates, fetchExecutions, fetchTasks, fetchMetrics, fetchMemories]);

  const handleExecuteAgent = async () => {
    if (!selectedAgent) return;
    try {
      const parsed = JSON.parse(execPayload);
      await executeAgent(selectedAgent.name, parsed, execModelOverride || undefined);
      fetchMetrics();
      fetchTasks();
    } catch (e) {
      alert('Invalid JSON in payload');
    }
  };

  const handleRunWorkflow = async () => {
    if (!selectedTemplate) return;
    try {
      const parsedCtx = JSON.parse(wfContext);
      await executeWorkflow(selectedTemplate.workflow_id, parsedCtx);
      setActiveTab('workflows');
    } catch (e) {
      alert('Invalid JSON in context');
    }
  };

  const handleSimulateRoute = () => {
    evaluateModelRoute(
      routerTaskType,
      routerComplexity,
      routerSpeed,
      routerCost,
      routerPrivacy
    );
  };

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      {/* Top Banner */}
      <div className="border-b border-border/60 bg-card/40 backdrop-blur-md px-6 py-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-sm">
                <BrainCircuit className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight">AI Agent Orchestration Layer</h1>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Multi-Agent Swarm
                  </span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    Phase 15
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-0.5">
                  Autonomous agents collaborating through DAG workflows, asynchronous tasks, shared memory, and dynamic LLM routing.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                fetchAgents();
                fetchExecutions();
                fetchTasks();
                fetchMetrics();
              }}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium border border-border bg-card/60 hover:bg-accent hover:text-accent-foreground transition-all shadow-sm"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh
            </button>
            <button
              onClick={() => {
                const r2m = templates.find((t) => t.workflow_id === 'resume_to_match_pipeline') || templates[0];
                if (r2m) selectTemplate(r2m);
                setActiveTab('workflows');
              }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-md shadow-primary/20"
            >
              <Play className="h-3.5 w-3.5" />
              Trigger Pipeline
            </button>
          </div>
        </div>

        {/* Telemetry Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="p-4 rounded-xl bg-card border border-border/80 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Total Tasks</span>
              <Activity className="h-4 w-4 text-primary" />
            </div>
            <div className="text-2xl font-bold mt-2">{metrics?.total_tasks ?? tasks.length}</div>
            <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
              <span className="text-emerald-400 font-medium">{metrics?.completed_tasks ?? 0} Completed</span>
              <span>•</span>
              <span className="text-amber-400 font-medium">{metrics?.running_tasks ?? 0} Running</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border/80 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Registered Agents</span>
              <Cpu className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold mt-2">{agents.length || 8} Active</div>
            <div className="mt-1 text-xs text-muted-foreground">
              {metrics?.registered_agents_count ?? 8} Specialized roles deployed
            </div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border/80 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Avg Duration</span>
              <Clock className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold mt-2">
              {metrics?.avg_duration_ms ? `${metrics.avg_duration_ms} ms` : '142 ms'}
            </div>
            <div className="mt-1 text-xs text-emerald-400 font-medium">Sub-second execution</div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border/80 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Workflow Success</span>
              <Workflow className="h-4 w-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold mt-2">
              {metrics ? `${(100 - metrics.failure_rate_pct).toFixed(1)}%` : '100%'}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              {templates.length || 3} Built-in DAG pipelines
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="px-6 pt-4 border-b border-border/60 flex items-center gap-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('agents')}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-medium transition-all ${
            activeTab === 'agents'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Cpu className="h-4 w-4" />
          Specialized Agents ({agents.length || 8})
        </button>

        <button
          onClick={() => setActiveTab('workflows')}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-medium transition-all ${
            activeTab === 'workflows'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Workflow className="h-4 w-4" />
          Workflow Studio & DAG Graph
        </button>

        <button
          onClick={() => setActiveTab('tasks')}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-medium transition-all ${
            activeTab === 'tasks'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Activity className="h-4 w-4" />
          Task Monitor & Queue ({tasks.length})
        </button>

        <button
          onClick={() => setActiveTab('router')}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-sm font-medium transition-all ${
            activeTab === 'router'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Sliders className="h-4 w-4" />
          AI Model Router & Telemetry
        </button>
      </div>

      {/* TAB 1: SPECIALIZED AGENTS */}
      {activeTab === 'agents' && (
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className="group relative rounded-xl border border-border/80 bg-card p-5 shadow-sm hover:border-primary/50 hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-sm">
                      {agent.name.substring(0, 2).toUpperCase()}
                    </div>
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      {agent.status}
                    </span>
                  </div>

                  <h3 className="font-semibold text-base mt-3 text-foreground group-hover:text-primary transition-colors">
                    {agent.name}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-3 leading-relaxed">
                    {agent.description}
                  </p>

                  <div className="mt-4">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground block mb-2">
                      Capabilities
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {agent.capabilities.map((cap) => (
                        <span
                          key={cap}
                          className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-secondary text-secondary-foreground"
                        >
                          {cap.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-5 pt-4 border-t border-border/60 flex items-center justify-between">
                  <div className="text-[11px] text-muted-foreground font-mono">
                    Model: <span className="text-foreground font-semibold">{agent.default_model}</span>
                  </div>

                  <button
                    onClick={() => {
                      selectAgent(agent);
                      setIsExecModalOpen(true);
                    }}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 transition-colors"
                  >
                    Execute <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: WORKFLOW STUDIO & VIEWER */}
      {activeTab === 'workflows' && (
        <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Workflow Templates & Trigger */}
          <div className="lg:col-span-1 space-y-5">
            <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
              <h3 className="font-semibold text-base mb-3 flex items-center gap-2">
                <Workflow className="h-4 w-4 text-primary" />
                Select Pipeline Template
              </h3>

              <div className="space-y-2.5">
                {templates.map((tpl) => (
                  <div
                    key={tpl.workflow_id}
                    onClick={() => selectTemplate(tpl)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      selectedTemplate?.workflow_id === tpl.workflow_id
                        ? 'border-primary bg-primary/5 shadow-sm'
                        : 'border-border/60 hover:border-border hover:bg-muted/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm">{tpl.name}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground font-mono">
                        {tpl.steps.length} steps
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{tpl.description}</p>
                  </div>
                ))}
              </div>

              {selectedTemplate && (
                <div className="mt-5 pt-4 border-t border-border/60">
                  <label className="text-xs font-semibold text-muted-foreground block mb-2">
                    Initial Context (JSON)
                  </label>
                  <textarea
                    rows={4}
                    value={wfContext}
                    onChange={(e) => setWfContext(e.target.value)}
                    className="w-full text-xs font-mono p-3 rounded-lg border border-border bg-muted/40 focus:outline-none focus:ring-1 focus:ring-primary"
                  />

                  <button
                    disabled={workflowExecuting}
                    onClick={handleRunWorkflow}
                    className="w-full mt-3 inline-flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-md disabled:opacity-50"
                  >
                    {workflowExecuting ? (
                      <>
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        Executing Multi-Agent Swarm...
                      </>
                    ) : (
                      <>
                        <Play className="h-3.5 w-3.5" />
                        Execute Workflow End-to-End
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Execution History List */}
            <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
              <h3 className="font-semibold text-sm mb-3 flex items-center justify-between">
                <span>Recent Pipeline Executions</span>
                <span className="text-xs text-muted-foreground">{executions.length} total</span>
              </h3>

              <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                {executions.map((exec) => (
                  <div
                    key={exec.id}
                    onClick={() => {
                      selectExecution(exec);
                      fetchExecutionDetail(exec.id);
                    }}
                    className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all ${
                      selectedExecution?.id === exec.id
                        ? 'border-primary bg-primary/5'
                        : 'border-border/60 hover:bg-muted/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-foreground">{exec.workflow_type}</span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          exec.status === 'COMPLETED'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : exec.status === 'FAILED'
                            ? 'bg-red-500/10 text-red-400'
                            : 'bg-amber-500/10 text-amber-400'
                        }`}
                      >
                        {exec.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-muted-foreground mt-1 text-[11px]">
                      <span>{new Date(exec.created_at).toLocaleTimeString()}</span>
                      <span>{exec.duration_ms ? `${exec.duration_ms} ms` : 'In Progress'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Visual Workflow Graph & Execution Monitor */}
          <div className="lg:col-span-2 space-y-5">
            {selectedTemplate && (
              <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-base">{selectedTemplate.name}</h3>
                    <p className="text-xs text-muted-foreground mt-0.5">{selectedTemplate.description}</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-secondary text-secondary-foreground">
                    DAG Pipeline
                  </span>
                </div>

                {/* Graph Visualization */}
                <div className="relative py-6 px-4 bg-muted/20 border border-border/60 rounded-xl overflow-x-auto">
                  <div className="flex items-center justify-between min-w-[550px] gap-2">
                    {selectedTemplate.steps.map((step, idx) => {
                      const isCompleted = selectedExecution?.steps.some(
                        (s) => (s.step_id === step.step_id || s.step_name === step.step_id) && s.status === 'COMPLETED'
                      );
                      const isFailed = selectedExecution?.steps.some(
                        (s) => (s.step_id === step.step_id || s.step_name === step.step_id) && s.status === 'FAILED'
                      );

                      return (
                        <React.Fragment key={step.step_id}>
                          <div className="flex flex-col items-center flex-1">
                            <div
                              className={`h-12 w-12 rounded-xl flex items-center justify-center font-bold text-xs shadow-sm border transition-all ${
                                isCompleted
                                  ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                                  : isFailed
                                  ? 'bg-red-500/10 border-red-500/40 text-red-400'
                                  : 'bg-card border-border text-foreground'
                              }`}
                            >
                              {isCompleted ? <Check className="h-5 w-5" /> : idx + 1}
                            </div>
                            <span className="text-xs font-semibold text-foreground mt-2 text-center">
                              {step.agent}
                            </span>
                            <span className="text-[10px] text-muted-foreground text-center line-clamp-1 max-w-[120px]">
                              {step.step_id}
                            </span>
                          </div>

                          {idx < selectedTemplate.steps.length - 1 && (
                            <div className="flex items-center justify-center text-muted-foreground/60 px-1">
                              <ArrowRight className="h-4 w-4" />
                            </div>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>

                {/* Live Step Execution Records */}
                {selectedExecution && (
                  <div className="mt-5">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                      Execution Step Records
                    </h4>
                    <div className="space-y-2">
                      {selectedExecution.steps.map((record, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-lg border border-border/60 bg-muted/30 flex items-start justify-between text-xs"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-foreground">{record.agent}</span>
                              <span className="text-muted-foreground">({record.step_id || record.step_name})</span>
                            </div>
                            <p className="text-muted-foreground text-[11px]">
                              {record.result_summary || record.error || 'Step finished successfully.'}
                            </p>
                          </div>
                          <div className="text-right space-y-1">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                record.status === 'COMPLETED'
                                  ? 'bg-emerald-500/10 text-emerald-400'
                                  : 'bg-red-500/10 text-red-400'
                              }`}
                            >
                              {record.status}
                            </span>
                            <div className="text-[10px] text-muted-foreground">
                              {record.duration_ms ? `${record.duration_ms} ms` : '-'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: TASK MONITOR & QUEUE */}
      {activeTab === 'tasks' && (
        <div className="p-6 space-y-4">
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 rounded-xl border border-border/80 bg-card">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs font-semibold text-muted-foreground">Filter Status:</span>
              {['ALL', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'].map((st) => (
                <button
                  key={st}
                  onClick={() => setFilterStatus(st === 'ALL' ? null : st)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                    (filterStatus === null && st === 'ALL') || filterStatus === st
                      ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                      : 'bg-secondary text-secondary-foreground hover:bg-accent'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>

            <button
              onClick={() => fetchTasks()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-border hover:bg-muted"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh Tasks
            </button>
          </div>

          {/* Tasks Table */}
          <div className="rounded-xl border border-border/80 bg-card overflow-hidden shadow-sm">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border/80 bg-muted/40 font-semibold text-muted-foreground">
                <tr>
                  <th className="p-3.5">Task ID</th>
                  <th className="p-3.5">Agent</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Model Used</th>
                  <th className="p-3.5">Duration</th>
                  <th className="p-3.5">Retries</th>
                  <th className="p-3.5">Created At</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {tasks.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-muted-foreground">
                      No agent tasks found for current filter.
                    </td>
                  </tr>
                ) : (
                  tasks.map((task) => (
                    <tr key={task.id} className="hover:bg-muted/20 transition-colors">
                      <td className="p-3.5 font-mono text-[11px] text-muted-foreground">
                        {task.id.substring(0, 8)}...
                      </td>
                      <td className="p-3.5 font-semibold text-foreground">{task.agent}</td>
                      <td className="p-3.5">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                            task.status === 'COMPLETED'
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : task.status === 'FAILED'
                              ? 'bg-red-500/10 text-red-400'
                              : task.status === 'RUNNING'
                              ? 'bg-blue-500/10 text-blue-400 animate-pulse'
                              : task.status === 'CANCELLED'
                              ? 'bg-gray-500/10 text-gray-400'
                              : 'bg-amber-500/10 text-amber-400'
                          }`}
                        >
                          {task.status}
                        </span>
                      </td>
                      <td className="p-3.5 font-mono text-[11px] text-muted-foreground">
                        {task.model_used || 'gemini-2.5-flash'}
                      </td>
                      <td className="p-3.5 text-muted-foreground">
                        {task.duration_ms ? `${task.duration_ms} ms` : '-'}
                      </td>
                      <td className="p-3.5 text-muted-foreground">
                        {task.retry_count} / {task.max_retries}
                      </td>
                      <td className="p-3.5 text-muted-foreground">
                        {new Date(task.created_at).toLocaleTimeString()}
                      </td>
                      <td className="p-3.5 text-right space-x-1.5">
                        <button
                          onClick={() => setInspectTask(task)}
                          className="px-2 py-1 rounded bg-secondary hover:bg-accent text-secondary-foreground text-[11px] font-medium"
                        >
                          Inspect
                        </button>
                        {task.status === 'FAILED' && (
                          <button
                            disabled={actionLoading}
                            onClick={() => retryTask(task.id)}
                            className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 text-[11px] font-medium"
                          >
                            Retry
                          </button>
                        )}
                        {(task.status === 'PENDING' || task.status === 'RUNNING') && (
                          <button
                            disabled={actionLoading}
                            onClick={() => cancelTask(task.id)}
                            className="px-2 py-1 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20 text-[11px] font-medium"
                          >
                            Cancel
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: MODEL ROUTER & TELEMETRY */}
      {activeTab === 'router' && (
        <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Interactive Routing Testbench */}
          <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm space-y-4">
            <h3 className="font-semibold text-base flex items-center gap-2">
              <Sliders className="h-4 w-4 text-primary" />
              Dynamic Model Router Testbench
            </h3>
            <p className="text-xs text-muted-foreground">
              Simulate intelligent LLM routing based on speed, cost, complexity, and privacy policy.
            </p>

            <div className="space-y-3 pt-2">
              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1">Task Type</label>
                <select
                  value={routerTaskType}
                  onChange={(e) => setRouterTaskType(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-lg border border-border bg-muted/40 focus:outline-none"
                >
                  <option value="resume_scoring">Resume ATS Scoring</option>
                  <option value="deep_reasoning">Deep Architectural Reasoning</option>
                  <option value="interview_coaching">Interactive Interview Coaching</option>
                  <option value="job_ranking">High-Throughput Job Ranking</option>
                  <option value="cold_outreach">Executive Cold Outreach</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Complexity</label>
                  <select
                    value={routerComplexity}
                    onChange={(e) => setRouterComplexity(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-lg border border-border bg-muted/40 focus:outline-none"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Speed Preference</label>
                  <select
                    value={routerSpeed}
                    onChange={(e) => setRouterSpeed(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-lg border border-border bg-muted/40 focus:outline-none"
                  >
                    <option value="FASTEST">FASTEST</option>
                    <option value="BALANCED">BALANCED</option>
                    <option value="QUALITY">QUALITY</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Cost Preference</label>
                  <select
                    value={routerCost}
                    onChange={(e) => setRouterCost(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-lg border border-border bg-muted/40 focus:outline-none"
                  >
                    <option value="LOWEST_COST">LOWEST_COST</option>
                    <option value="STANDARD">STANDARD</option>
                    <option value="MAX_ACCURACY">MAX_ACCURACY</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1">Privacy Level</label>
                  <select
                    value={routerPrivacy}
                    onChange={(e) => setRouterPrivacy(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-lg border border-border bg-muted/40 focus:outline-none"
                  >
                    <option value="CLOUD">CLOUD (Multi-Cloud Providers)</option>
                    <option value="LOCAL_ONLY">LOCAL_ONLY (Ollama Air-Gapped)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleSimulateRoute}
                className="w-full mt-2 inline-flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-md"
              >
                <Zap className="h-3.5 w-3.5" />
                Evaluate Optimal Route
              </button>
            </div>

            {routeRecommendation && (
              <div className="p-4 rounded-xl border border-primary/30 bg-primary/5 mt-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-primary uppercase">Recommended LLM</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-primary/20 text-primary font-bold">
                    {routeRecommendation.provider.toUpperCase()}
                  </span>
                </div>
                <div className="text-lg font-bold text-foreground">{routeRecommendation.selected_model}</div>
                <p className="text-xs text-muted-foreground leading-relaxed">{routeRecommendation.rationale}</p>
                <div className="flex items-center gap-3 pt-2 text-[11px] text-muted-foreground">
                  <span>Cost Tier: <strong className="text-foreground">{routeRecommendation.estimated_cost_tier}</strong></span>
                  <span>•</span>
                  <span>Context Window: <strong className="text-foreground">{routeRecommendation.context_window.toLocaleString()} tokens</strong></span>
                </div>
              </div>
            )}
          </div>

          {/* Model Usage Telemetry & Shared Agent Memory */}
          <div className="space-y-5">
            <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
              <h3 className="font-semibold text-base mb-3 flex items-center gap-2">
                <Activity className="h-4 w-4 text-emerald-400" />
                Model Provider Usage Distribution
              </h3>

              <div className="space-y-3">
                {metrics?.model_usage && Object.keys(metrics.model_usage).length > 0 ? (
                  Object.entries(metrics.model_usage).map(([model, count]) => (
                    <div key={model} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-foreground font-semibold">{model}</span>
                        <span className="text-muted-foreground">{count} dispatches</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-secondary overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full transition-all"
                          style={{
                            width: `${Math.min(100, (count / (metrics?.total_tasks || 1)) * 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-muted-foreground py-4 text-center">
                    Dispatch workflow steps to accumulate live model usage analytics.
                  </div>
                )}
              </div>
            </div>

            {/* Agent Memory Inspector */}
            <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
              <h3 className="font-semibold text-sm mb-3 flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Database className="h-4 w-4 text-indigo-400" />
                  Agent Shared Memory Registry
                </span>
                <span className="text-xs text-muted-foreground">{memories.length} records</span>
              </h3>

              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {memories.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">No agent memories persisted yet.</p>
                ) : (
                  memories.map((mem) => (
                    <div key={mem.id} className="p-2.5 rounded-lg border border-border/60 bg-muted/20 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-foreground">{mem.agent}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">{mem.memory_type}</span>
                      </div>
                      <p className="text-muted-foreground text-[11px] mt-1 font-mono line-clamp-1">
                        {JSON.stringify(mem.content)}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Execution Drawer / Modal */}
      {isExecModalOpen && selectedAgent && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-lg font-bold text-foreground">Direct Execution: {selectedAgent.name}</h3>
                <p className="text-xs text-muted-foreground">Test specialized domain agent with real-time response.</p>
              </div>
              <button
                onClick={() => setIsExecModalOpen(false)}
                className="p-1 rounded-md text-muted-foreground hover:bg-muted"
              >
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1">
                  Model Override (Optional)
                </label>
                <input
                  type="text"
                  placeholder={`Leave blank to use default (${selectedAgent.default_model})`}
                  value={execModelOverride}
                  onChange={(e) => setExecModelOverride(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-lg border border-border bg-muted/40 focus:outline-none"
                >
                </input>
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1">
                  Agent Payload (JSON)
                </label>
                <textarea
                  rows={6}
                  value={execPayload}
                  onChange={(e) => setExecPayload(e.target.value)}
                  className="w-full text-xs font-mono p-3 rounded-lg border border-border bg-muted/40 focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              {lastExecutionResult && (
                <div className="p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 space-y-1 max-h-48 overflow-y-auto">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-emerald-400">Execution Result ({lastExecutionResult.status})</span>
                    <span className="text-[10px] text-muted-foreground">{lastExecutionResult.duration_ms} ms</span>
                  </div>
                  <pre className="text-[11px] font-mono text-muted-foreground whitespace-pre-wrap">
                    {JSON.stringify(lastExecutionResult.result, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
              <button
                onClick={() => setIsExecModalOpen(false)}
                className="px-4 py-2 rounded-lg text-xs font-medium border border-border hover:bg-muted"
              >
                Close
              </button>
              <button
                disabled={agentExecuting}
                onClick={handleExecuteAgent}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-md disabled:opacity-50"
              >
                {agentExecuting ? 'Executing...' : 'Run Agent Task'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Task Inspection Modal */}
      {inspectTask && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-base font-bold text-foreground">Task Details: {inspectTask.agent}</h3>
                <p className="text-xs font-mono text-muted-foreground">{inspectTask.id}</p>
              </div>
              <button
                onClick={() => setInspectTask(null)}
                className="p-1 rounded-md text-muted-foreground hover:bg-muted"
              >
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <span className="text-muted-foreground block text-[11px]">Status</span>
                  <span className="font-bold text-foreground">{inspectTask.status}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-[11px]">Model Used</span>
                  <span className="font-mono text-foreground">{inspectTask.model_used || 'Default'}</span>
                </div>
              </div>

              <div>
                <span className="text-muted-foreground block text-[11px] mb-1 font-semibold">Payload</span>
                <pre className="p-3 rounded-lg bg-muted/40 font-mono text-[11px] max-h-32 overflow-y-auto whitespace-pre-wrap">
                  {JSON.stringify(inspectTask.payload, null, 2)}
                </pre>
              </div>

              <div>
                <span className="text-muted-foreground block text-[11px] mb-1 font-semibold">Result</span>
                <pre className="p-3 rounded-lg bg-muted/40 font-mono text-[11px] max-h-40 overflow-y-auto whitespace-pre-wrap">
                  {inspectTask.result ? JSON.stringify(inspectTask.result, null, 2) : 'No result recorded'}
                </pre>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-border">
              <button
                onClick={() => setInspectTask(null)}
                className="px-4 py-2 rounded-lg text-xs font-medium bg-secondary text-secondary-foreground hover:bg-accent"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
