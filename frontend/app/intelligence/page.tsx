'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useIntelligenceStore } from '@/store/intelligence-store';
import {
  OutcomeTrendsChart,
  ResumePerformanceChart,
  SkillImpactChart,
  CompanyResponseChart,
  RecordOutcomeModal,
} from '@/features/intelligence';
import {
  AlertCircle,
  Award,
  BarChart3,
  Brain,
  Briefcase,
  Building2,
  Calendar,
  CheckCircle2,
  Clock,
  Compass,
  FileText,
  Filter,
  Layers,
  Lightbulb,
  PlusCircle,
  RefreshCw,
  Sparkles,
  Target,
  TrendingUp,
  XCircle,
} from 'lucide-react';

export default function CareerIntelligencePage() {
  const {
    overview,
    analytics,
    outcomes,
    resumes,
    skills,
    companies,
    recommendations,
    trends,
    loading,
    error,
    fetchOverview,
    fetchOutcomes,
    fetchTrends,
    recordOutcome,
    createSnapshot,
  } = useIntelligenceStore();

  const [activeTab, setActiveTab] = React.useState<
    'overview' | 'outcomes' | 'resumes' | 'skills' | 'companies'
  >('overview');
  const [outcomeModalOpen, setOutcomeModalOpen] = React.useState(false);
  const [outcomeFilter, setOutcomeFilter] = React.useState<string>('all');
  const [snapshotSuccess, setSnapshotSuccess] = React.useState(false);

  React.useEffect(() => {
    fetchOverview();
    fetchOutcomes();
    fetchTrends(90);
  }, [fetchOverview, fetchOutcomes, fetchTrends]);

  const handleRefresh = async () => {
    await Promise.all([fetchOverview(), fetchOutcomes(), fetchTrends(90)]);
  };

  const handleCreateSnapshot = async () => {
    const success = await createSnapshot();
    if (success) {
      setSnapshotSuccess(true);
      setTimeout(() => setSnapshotSuccess(false), 3000);
    }
  };

  const filteredOutcomes = React.useMemo(() => {
    if (outcomeFilter === 'all') return outcomes;
    return outcomes.filter((o) => o.outcomeType === outcomeFilter);
  }, [outcomes, outcomeFilter]);

  const summary = overview?.analytics || analytics;

  return (
    <AppShell>
      <PageHeader
        title="Career Intelligence & Outcome Learning"
        description="Learn from real hiring outcomes: correlate interview and offer conversion with resumes, competencies, employers, and application strategies."
        badge={
          <Badge variant="outline" className="font-mono text-xs gap-1 border-primary/30 text-primary">
            <Brain className="h-3 w-3" />
            Outcome Feedback Loop
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCreateSnapshot}
              disabled={loading}
              className="gap-1.5 text-xs"
            >
              {snapshotSuccess ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  Snapshot Saved!
                </>
              ) : (
                <>
                  <Layers className="h-3.5 w-3.5" />
                  Save Snapshot
                </>
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
              className="gap-1 text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={() => setOutcomeModalOpen(true)}
              className="gap-1.5 text-xs bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <PlusCircle className="h-3.5 w-3.5" />
              Record Outcome
            </Button>
          </div>
        }
      />

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-sm text-rose-400">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="outline" size="sm" onClick={handleRefresh} className="h-7 text-xs">
            Retry
          </Button>
        </div>
      )}

      {/* Top Level Key Telemetry Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="bg-card/40 border-border/60">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Total Applications
              </span>
              <Briefcase className="h-4 w-4 text-blue-400" />
            </div>
            <div className="mt-2 text-2xl font-bold">{summary?.totalApplications ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {summary?.totalOutcomes ?? 0} documented milestone outcomes
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/60">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Interview Rate
              </span>
              <Award className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="mt-2 text-2xl font-bold text-emerald-400">
              {summary ? (summary.interviewRate * 100).toFixed(1) : '0.0'}%
            </div>
            <div className="mt-1.5 h-1.5 w-full bg-muted/40 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full"
                style={{ width: `${Math.min(100, (summary?.interviewRate ?? 0) * 100)}%` }}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/60">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Offer Rate
              </span>
              <Sparkles className="h-4 w-4 text-purple-400" />
            </div>
            <div className="mt-2 text-2xl font-bold text-purple-400">
              {summary ? (summary.offerRate * 100).toFixed(1) : '0.0'}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {summary?.offersReceived ?? 0} received formal offers
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/60">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Avg Turnaround
              </span>
              <Clock className="h-4 w-4 text-amber-400" />
            </div>
            <div className="mt-2 text-2xl font-bold">
              {summary?.avgResponseDays ?? 0}{' '}
              <span className="text-xs font-normal text-muted-foreground">days</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Median: {summary?.medianResponseDays ?? 0} days</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs Bar */}
      <div className="flex items-center border-b border-border/60 mb-6 gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'overview'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Lightbulb className="h-4 w-4" />
          Recommendations & Insights
        </button>
        <button
          onClick={() => setActiveTab('outcomes')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'outcomes'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <TrendingUp className="h-4 w-4" />
          Outcome Analytics & Funnel
        </button>
        <button
          onClick={() => setActiveTab('resumes')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'resumes'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileText className="h-4 w-4" />
          Resume Effectiveness
        </button>
        <button
          onClick={() => setActiveTab('skills')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'skills'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Sparkles className="h-4 w-4" />
          Skill Impact Matrix
        </button>
        <button
          onClick={() => setActiveTab('companies')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'companies'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Building2 className="h-4 w-4" />
          Companies & Strategy
        </button>
      </div>

      {/* TAB 1: OVERVIEW & EVIDENCE-BASED RECOMMENDATIONS */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8">
              <OutcomeTrendsChart data={trends} loading={loading} />
            </div>

            <div className="lg:col-span-4">
              <Card className="h-full flex flex-col justify-between">
                <CardHeader>
                  <CardTitle className="text-base font-semibold flex items-center gap-2">
                    <Compass className="h-4 w-4 text-primary" />
                    Pipeline Conversion Funnel
                  </CardTitle>
                  <CardDescription>Real-time candidate stages across tracked roles</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { key: 'APPLIED', label: 'Submitted / In Review', color: 'bg-blue-500' },
                    { key: 'ASSESSMENT', label: 'Technical Assessment', color: 'bg-cyan-500' },
                    { key: 'INTERVIEW', label: 'Interview Scheduled', color: 'bg-emerald-500' },
                    { key: 'OFFER', label: 'Formal Offer', color: 'bg-purple-500' },
                    { key: 'REJECTED', label: 'Declined / Archived', color: 'bg-rose-500' },
                  ].map((stage) => {
                    const count = summary?.activeFunnel?.[stage.key] || 0;
                    const pct = summary?.totalApplications
                      ? Math.round((count / summary.totalApplications) * 100)
                      : 0;
                    return (
                      <div key={stage.key} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span>{stage.label}</span>
                          <span className="text-muted-foreground">
                            {count} ({pct}%)
                          </span>
                        </div>
                        <div className="h-2 w-full bg-muted/40 rounded-full overflow-hidden">
                          <div className={`h-full ${stage.color} rounded-full`} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Actionable Recommendations Grounded in Observed Data */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-amber-400" />
                  Evidence-Based Strategic Recommendations
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Guidance derived strictly from empirical conversion correlations in your application data
                </p>
              </div>
            </div>

            {recommendations.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center text-muted-foreground">
                  <Lightbulb className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No recommendations generated yet</p>
                  <p className="text-xs mt-1">Submit applications and log outcomes to unlock insights</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.map((rec) => (
                  <Card key={rec.id} className="border-border/60 hover:border-primary/40 transition-colors">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <Badge
                          variant="outline"
                          className={
                            rec.category === 'SKILL'
                              ? 'border-purple-500/30 text-purple-400 bg-purple-500/10'
                              : rec.category === 'RESUME'
                              ? 'border-blue-500/30 text-blue-400 bg-blue-500/10'
                              : rec.category === 'STRATEGY'
                              ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
                              : 'border-amber-500/30 text-amber-400 bg-amber-500/10'
                          }
                        >
                          {rec.category}
                        </Badge>
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <span>Impact:</span>
                          <span
                            className={
                              rec.impactLevel === 'HIGH'
                                ? 'text-emerald-400 font-semibold'
                                : rec.impactLevel === 'MEDIUM'
                                ? 'text-amber-400 font-medium'
                                : 'text-slate-400'
                            }
                          >
                            {rec.impactLevel}
                          </span>
                        </div>
                      </div>
                      <CardTitle className="text-sm font-semibold mt-2">{rec.title}</CardTitle>
                      <CardDescription className="text-xs leading-relaxed">{rec.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3 pt-1">
                      <div className="p-2.5 rounded-md bg-muted/30 border border-border/40 text-xs">
                        <span className="font-semibold text-muted-foreground block mb-0.5">
                          Empirical Evidence:
                        </span>
                        <p className="text-foreground/90 font-mono text-[11px]">{rec.evidence}</p>
                      </div>
                      <div className="flex items-center justify-between text-xs pt-1">
                        <span className="text-muted-foreground">Suggested Action:</span>
                        <span className="font-medium text-primary text-right">{rec.actionSuggested}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: OUTCOMES & FUNNEL */}
      {activeTab === 'outcomes' && (
        <div className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold">Outcome Event History</CardTitle>
                <CardDescription>Chronological milestones and feedback logged for tracked jobs</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Filter className="h-3.5 w-3.5 text-muted-foreground" />
                <select
                  value={outcomeFilter}
                  onChange={(e) => setOutcomeFilter(e.target.value)}
                  className="bg-background border border-border rounded-md px-2.5 py-1 text-xs focus:outline-none"
                >
                  <option value="all">All Outcome Types</option>
                  <option value="InterviewReceived">Interviews</option>
                  <option value="AssessmentReceived">Assessments</option>
                  <option value="OfferReceived">Offers</option>
                  <option value="Rejected">Rejections</option>
                  <option value="Withdrawn">Withdrawn</option>
                </select>
              </div>
            </CardHeader>
            <CardContent>
              {filteredOutcomes.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground border border-dashed rounded-lg">
                  <p className="text-sm">No outcome events logged matching this filter</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setOutcomeModalOpen(true)}
                    className="mt-3 gap-1 text-xs"
                  >
                    <PlusCircle className="h-3.5 w-3.5" />
                    Record First Outcome
                  </Button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="border-b border-border/60 text-muted-foreground uppercase text-[10px] tracking-wider">
                      <tr>
                        <th className="py-2.5 px-3">Milestone</th>
                        <th className="py-2.5 px-3">Role / Opportunity</th>
                        <th className="py-2.5 px-3">Company</th>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Notes / Context</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/40">
                      {filteredOutcomes.map((evt) => (
                        <tr key={evt.id} className="hover:bg-muted/20">
                          <td className="py-2.5 px-3 font-medium">
                            <Badge
                              variant="outline"
                              className={
                                evt.outcomeType === 'InterviewReceived'
                                  ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
                                  : evt.outcomeType === 'OfferReceived'
                                  ? 'border-purple-500/30 text-purple-400 bg-purple-500/10'
                                  : evt.outcomeType === 'AssessmentReceived'
                                  ? 'border-blue-500/30 text-blue-400 bg-blue-500/10'
                                  : evt.outcomeType === 'Rejected'
                                  ? 'border-rose-500/30 text-rose-400 bg-rose-500/10'
                                  : 'border-slate-500/30 text-slate-400 bg-slate-500/10'
                              }
                            >
                              {evt.outcomeType}
                            </Badge>
                          </td>
                          <td className="py-2.5 px-3 font-medium">{evt.jobTitle || 'Application'}</td>
                          <td className="py-2.5 px-3 text-muted-foreground">{evt.company || '—'}</td>
                          <td className="py-2.5 px-3 text-muted-foreground">
                            {new Date(evt.occurredAt).toLocaleDateString()}
                          </td>
                          <td className="py-2.5 px-3 max-w-xs truncate text-muted-foreground">
                            {evt.notes || '—'}
                          </td>
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

      {/* TAB 3: RESUME EFFECTIVENESS */}
      {activeTab === 'resumes' && (
        <div className="space-y-6">
          <ResumePerformanceChart data={resumes} loading={loading} />

          <div>
            <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground mb-3">
              Tailored Resume Variant Performance
            </h3>
            {resumes.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center text-muted-foreground">
                  <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No tailored resume versions benchmarked yet</p>
                  <p className="text-xs mt-1">Generate tailored resumes to track A/B performance</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {resumes.map((r) => (
                  <Card key={r.id} className="border-border/60">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-[10px]">
                          ATS Score: {r.atsScore ? `${r.atsScore.toFixed(0)}%` : 'N/A'}
                        </Badge>
                        <span className="text-xs font-bold text-emerald-400">
                          {(r.responseRate * 100).toFixed(1)}% Response
                        </span>
                      </div>
                      <CardTitle className="text-sm font-semibold mt-2">{r.resumeTitle || 'Tailored Resume'}</CardTitle>
                      <CardDescription className="text-xs">{r.targetRole || 'Target Role'}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2 text-xs pt-1">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Applications Sent:</span>
                        <span className="font-semibold">{r.applicationsSent}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Interviews Received:</span>
                        <span className="font-semibold text-emerald-400">{r.interviewsReceived}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Offers Extended:</span>
                        <span className="font-semibold text-purple-400">{r.offersReceived}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: SKILL IMPACT MATRIX */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          <div className="p-3.5 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-start gap-2.5 text-xs text-blue-300">
            <Sparkles className="h-4 w-4 shrink-0 mt-0.5 text-blue-400" />
            <p>
              <strong>Descriptive Analytics Notice:</strong> Competency influence scores reflect empirical
              correlations observed strictly within your submitted application history. These metrics do not
              constitute causal guarantees for future hiring decisions.
            </p>
          </div>

          <SkillImpactChart data={skills} loading={loading} />

          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Skill Impact Leaderboard</CardTitle>
              <CardDescription>
                Detailed correlation scores between candidate competencies and positive hiring decisions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {skills.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">
                  <p className="text-sm">No skill impact metrics computed yet</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="border-b border-border/60 text-muted-foreground uppercase text-[10px] tracking-wider">
                      <tr>
                        <th className="py-2.5 px-3">Skill / Competency</th>
                        <th className="py-2.5 px-3">Interviews Influenced</th>
                        <th className="py-2.5 px-3">Offers Influenced</th>
                        <th className="py-2.5 px-3">Avg Match Score</th>
                        <th className="py-2.5 px-3">Correlation Score</th>
                        <th className="py-2.5 px-3">Recommendation Weight</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/40">
                      {skills.map((s) => (
                        <tr key={s.id} className="hover:bg-muted/20">
                          <td className="py-2.5 px-3 font-semibold">{s.skillName}</td>
                          <td className="py-2.5 px-3 text-emerald-400 font-bold">{s.interviewsInfluenced}</td>
                          <td className="py-2.5 px-3 text-purple-400 font-bold">{s.offersInfluenced}</td>
                          <td className="py-2.5 px-3 font-mono">{s.averageMatchScore.toFixed(1)}%</td>
                          <td className="py-2.5 px-3 font-mono">
                            <span
                              className={
                                s.correlationScore > 0
                                  ? 'text-emerald-400'
                                  : s.correlationScore < 0
                                  ? 'text-rose-400'
                                  : 'text-muted-foreground'
                              }
                            >
                              {s.correlationScore > 0 ? `+${s.correlationScore}` : s.correlationScore}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <Badge
                              variant="outline"
                              className={
                                s.recommendationWeight === 'CRITICAL'
                                  ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10'
                                  : s.recommendationWeight === 'HIGH'
                                  ? 'border-purple-500/40 text-purple-400 bg-purple-500/10'
                                  : s.recommendationWeight === 'MODERATE'
                                  ? 'border-blue-500/40 text-blue-400 bg-blue-500/10'
                                  : 'border-slate-500/40 text-slate-400'
                              }
                            >
                              {s.recommendationWeight}
                            </Badge>
                          </td>
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

      {/* TAB 5: COMPANIES & STRATEGY */}
      {activeTab === 'companies' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6">
              <CompanyResponseChart data={companies} loading={loading} />
            </div>

            <div className="lg:col-span-6">
              <Card className="h-full">
                <CardHeader>
                  <CardTitle className="text-base font-semibold flex items-center gap-2">
                    <Target className="h-4 w-4 text-primary" />
                    Channel & Source Yield
                  </CardTitle>
                  <CardDescription>Interview conversion rate across application channels</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {overview?.strategy?.sourceBreakdown.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-6">
                      No channel breakdown telemetry available
                    </p>
                  ) : (
                    overview?.strategy?.sourceBreakdown.map((s) => (
                      <div key={s.source} className="p-3 rounded-lg border border-border/60 bg-muted/20">
                        <div className="flex items-center justify-between mb-1 text-xs">
                          <span className="font-semibold">{s.source}</span>
                          <span className="text-emerald-400 font-bold">
                            {(s.response_rate * 100).toFixed(1)}% Interview Rate
                          </span>
                        </div>
                        <div className="flex justify-between text-[11px] text-muted-foreground">
                          <span>{s.sent} submissions</span>
                          <span>{s.interviews} interview(s)</span>
                        </div>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Key Strategic Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-amber-400" />
                Strategic Optimization Takeaways
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-xs">
                {overview?.strategy?.keyInsights.map((insight, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                    <span className="leading-relaxed">{insight}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Record Outcome Modal */}
      <RecordOutcomeModal
        isOpen={outcomeModalOpen}
        onClose={() => setOutcomeModalOpen(false)}
        onSubmit={recordOutcome}
      />
    </AppShell>
  );
}
