'use client';

import React from 'react';
import {
  Calendar,
  CheckCircle2,
  Sparkles,
  BookOpen,
  ArrowUpRight,
  TrendingUp,
  Target,
  Clock,
  Compass,
} from 'lucide-react';
import { CareerCoaching } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface CoachingRoadmapProps {
  coaching: CareerCoaching | null;
  loading?: boolean;
}

export function CoachingRoadmap({ coaching, loading = false }: CoachingRoadmapProps) {
  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-6 w-48 bg-muted rounded mb-2" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="p-4 border-border/40 bg-card/60">
              <div className="h-4 w-24 bg-muted rounded mb-2" />
              <div className="h-16 bg-muted/50 rounded" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!coaching) {
    return null;
  }

  const roadmap = coaching.learningRoadmap || [];
  const recommendations = coaching.skillDevelopmentRecommendations || [];

  const getPriorityBadge = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'low':
      default:
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* 4-Week Structured Roadmap */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-primary" />
            <h3 className="text-base font-bold text-foreground">
              Personalized Interview Preparation Roadmap
            </h3>
          </div>
          <span className="text-xs text-muted-foreground hidden sm:inline">
            Role: <strong className="text-foreground">{coaching.role}</strong>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {roadmap.map((step, idx) => (
            <Card
              key={idx}
              className="p-4 border-border/60 bg-card/70 backdrop-blur-sm hover:border-primary/50 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 text-xs font-semibold">
                    {step.phase || `Phase ${idx + 1}`}
                  </Badge>
                  <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                    <Calendar className="w-3 h-3" /> {step.duration || '1 week'}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-foreground mb-1">
                  {step.title}
                </h4>

                <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                  {step.focus}
                </p>

                {step.milestones && step.milestones.length > 0 && (
                  <div className="space-y-1 mb-3">
                    <span className="text-[11px] font-semibold text-foreground/80 block uppercase tracking-wider">
                      Key Milestones:
                    </span>
                    <ul className="text-xs text-muted-foreground space-y-1 pl-4 list-disc">
                      {step.milestones.map((m, i) => (
                        <li key={i} className="leading-snug">{m}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="mt-3 pt-2.5 border-t border-border/40 text-[11px] text-primary/90 font-medium flex items-center gap-1">
                <Target className="w-3.5 h-3.5 shrink-0" />
                <span>Structured preparation target</span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Prioritized Skill Development Recommendations */}
      {recommendations.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-foreground">
              Skill Development Recommendations & Target Growth
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {recommendations.map((rec, idx) => (
              <Card
                key={idx}
                className="p-3.5 border-border/50 bg-card/60 backdrop-blur-sm hover:border-border transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-foreground">
                      {rec.skill}
                    </span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-semibold uppercase tracking-wider py-0.5 ${getPriorityBadge(
                        rec.priority
                      )}`}
                    >
                      {rec.priority} Priority
                    </Badge>
                  </div>

                  <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                    {rec.action}
                  </p>
                </div>

                <div className="pt-2 border-t border-border/40 flex items-center justify-between text-[11px] text-muted-foreground mt-2">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-primary" />
                    Est: {rec.estimatedDays} days
                  </span>
                  <span className="text-primary font-medium flex items-center gap-0.5">
                    Plan <ArrowUpRight className="w-3 h-3" />
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
