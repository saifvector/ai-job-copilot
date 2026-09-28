'use client';

import * as React from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardStore } from '@/store/dashboard-store';
import {
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Code2,
  ExternalLink,
  FileText,
  GraduationCap,
  HeartPulse,
  LayoutDashboard,
  Lightbulb,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

export default function ProfileHealthPage() {
  const { profileHealth, loading, fetchProfileHealth } = useDashboardStore();

  React.useEffect(() => {
    fetchProfileHealth();
  }, [fetchProfileHealth]);

  const overall = profileHealth?.overallScore ?? 0;
  const breakdown = profileHealth?.breakdown ?? {
    resumeCompleteness: 0,
    skillCoverage: 0,
    experienceCoverage: 0,
    educationCoverage: 0,
  };

  const pillars = [
    {
      title: 'Resume Document & Header',
      weight: '25% Weight',
      score: breakdown.resumeCompleteness,
      icon: FileText,
      color: 'bg-emerald-500',
      description:
        'Validates uploaded resume PDF/DOCX, target roles, location preferences, and executive summary statement.',
      actionHref: '/resume',
      actionLabel: 'Manage Resume',
    },
    {
      title: 'Technical & Domain Skills',
      weight: '25% Weight',
      score: breakdown.skillCoverage,
      icon: Code2,
      color: 'bg-blue-500',
      description:
        'Evaluates total volume of extracted competencies, multi-category diversity, and confidence ratings.',
      actionHref: '/profile',
      actionLabel: 'Review Skills',
    },
    {
      title: 'Professional Experience Depth',
      weight: '25% Weight',
      score: breakdown.experienceCoverage,
      icon: Briefcase,
      color: 'bg-indigo-500',
      description:
        'Analyzes documented employment positions, tenure continuity, and impact descriptions.',
      actionHref: '/profile',
      actionLabel: 'Update Experience',
    },
    {
      title: 'Academic & Accreditation',
      weight: '25% Weight',
      score: breakdown.educationCoverage,
      icon: GraduationCap,
      color: 'bg-amber-500',
      description:
        'Checks academic degree levels, institution verification, fields of study, and industry certifications.',
      actionHref: '/profile',
      actionLabel: 'Add Education',
    },
  ];

  return (
    <AppShell>
      <PageHeader
        title="Profile Health Audit"
        description="Comprehensive diagnostic evaluation of candidate profile completeness and AI matching calibration."
        badge={
          <Badge variant="outline" className="font-mono text-xs">
            Profile Optimization
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchProfileHealth()}
              disabled={loading}
              className="h-8 gap-1.5 text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Re-evaluate
            </Button>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-md text-xs font-medium h-8 px-3 border border-border bg-background hover:bg-muted text-foreground transition-colors"
            >
              <LayoutDashboard className="h-3.5 w-3.5 mr-1.5" />
              Dashboard
            </Link>
          </div>
        }
      />

      <div className="space-y-6">
        {/* Overall Health Hero Header */}
        <Card className="border-border/80 bg-card/60">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
              <div className="space-y-2 max-w-xl">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-500 border border-rose-500/20 text-xs font-medium">
                  <HeartPulse className="h-3.5 w-3.5" />
                  Health Calibration Index
                </div>
                <h2 className="text-2xl font-bold tracking-tight text-foreground">
                  Overall Profile Score: <span className="text-primary font-mono">{overall}%</span>
                </h2>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Calculated from a 4-pillar algorithmic evaluation (Resume, Skills, Experience, Education).
                  Each pillar contributes 25% toward matching precision. Profiles scoring above 80% achieve
                  substantially higher placement compatibility.
                </p>
              </div>

              <div className="flex items-center gap-4 self-center sm:self-auto">
                <div className="relative h-28 w-28 rounded-full border-8 border-muted flex items-center justify-center font-mono font-bold text-2xl text-foreground">
                  <div
                    className="absolute inset-0 rounded-full border-8 border-primary border-t-transparent animate-spin-slow"
                    style={{
                      transform: `rotate(${(overall / 100) * 360}deg)`,
                      transition: 'transform 1s ease-out',
                    }}
                  />
                  {overall}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 4 Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pillars.map((p) => {
            const Icon = p.icon;
            return (
              <Card key={p.title} className="flex flex-col justify-between">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-muted/50 text-foreground">
                        <Icon className="h-4 w-4" />
                      </div>
                      <CardTitle className="text-sm font-semibold">{p.title}</CardTitle>
                    </div>
                    <span className="text-xs font-mono font-bold text-foreground">{p.score}%</span>
                  </div>
                  <CardDescription className="text-xs">{p.description}</CardDescription>
                </CardHeader>

                <CardContent className="space-y-4 pt-1">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                      <span>Pillar Score</span>
                      <span className="font-mono">{p.score} / 100</span>
                    </div>
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${p.color} transition-all duration-500`}
                        style={{ width: `${p.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-border/50">
                    <span className="text-[11px] text-muted-foreground font-mono">{p.weight}</span>
                    <Link
                      href={p.actionHref}
                      className="inline-flex items-center text-xs font-medium text-primary hover:underline"
                    >
                      {p.actionLabel}
                      <ArrowRight className="h-3 w-3 ml-1" />
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Strengths & Actionable Recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strengths */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2 text-emerald-500">
                <ShieldCheck className="h-4 w-4" />
                Validated Profile Strengths
              </CardTitle>
              <CardDescription>Areas currently calibrated at high strength</CardDescription>
            </CardHeader>
            <CardContent>
              {profileHealth?.strengths && profileHealth.strengths.length > 0 ? (
                <ul className="space-y-2 text-xs">
                  {profileHealth.strengths.map((str, i) => (
                    <li key={i} className="flex items-start gap-2 p-2 rounded-md bg-emerald-500/5 text-foreground">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0 mt-0.5" />
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-muted-foreground py-4 text-center">
                  Upload a resume and add verified skills to unlock strengths analysis.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Actionable Recommendations Checklist */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2 text-primary">
                <Lightbulb className="h-4 w-4 text-amber-500" />
                Optimization Action Plan
              </CardTitle>
              <CardDescription>Steps recommended to elevate your score to 100%</CardDescription>
            </CardHeader>
            <CardContent>
              {profileHealth?.actionableRecommendations && profileHealth.actionableRecommendations.length > 0 ? (
                <ul className="space-y-2 text-xs">
                  {profileHealth.actionableRecommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2 p-2 rounded-md bg-muted/40 text-foreground">
                      <span className="flex h-4 w-4 rounded-full bg-primary/10 text-primary text-[10px] items-center justify-center font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-emerald-500 py-4 text-center font-medium">
                  Your profile is fully optimized across all 4 pillars!
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
