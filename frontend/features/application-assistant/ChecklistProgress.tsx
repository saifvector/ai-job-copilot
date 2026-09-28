'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ChecklistResponse } from '@/types';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  FileCheck,
  ShieldCheck,
  ArrowRight,
} from 'lucide-react';

interface ChecklistProgressProps {
  checklist: ChecklistResponse | null;
  onNavigateToStep?: (step: number) => void;
}

export const ChecklistProgress: React.FC<ChecklistProgressProps> = ({
  checklist,
  onNavigateToStep,
}) => {
  const score = Math.round(checklist?.readinessScore ?? 0);
  const isReady = checklist?.isReadyForReview ?? (score >= 80);
  const items = checklist?.items ?? [];
  const missingFields = checklist?.missingFields ?? [];

  const getScoreColor = (sc: number) => {
    if (sc >= 80) return 'text-emerald-600 dark:text-emerald-400';
    if (sc >= 50) return 'text-amber-500 dark:text-amber-400';
    return 'text-rose-500 dark:text-rose-400';
  };

  return (
    <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm mb-6">
      <CardHeader className="p-5 pb-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <CardTitle className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              Application Readiness Checklist
            </CardTitle>
            <CardDescription className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Automated audit verifying document attachment, required questions, and profile integrity.
            </CardDescription>
          </div>

          <div className="flex items-center gap-2">
            <span className={`text-2xl font-black ${getScoreColor(score)}`}>
              {score}%
            </span>
            <Badge variant={isReady ? 'success' : 'secondary'} className="text-xs">
              {isReady ? 'Ready for Review' : 'Incomplete'}
            </Badge>
          </div>
        </div>

        <div className="mt-3">
          <Progress value={score} className="h-2" />
        </div>
      </CardHeader>

      <CardContent className="p-5 pt-3 space-y-4">
        {/* Missing Fields Box */}
        {missingFields.length > 0 && (
          <div className="p-3.5 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-900/50">
            <div className="flex items-center gap-2 mb-2 text-xs font-bold text-amber-800 dark:text-amber-300">
              <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              Missing Information Identified ({missingFields.length})
            </div>
            <ul className="space-y-1 text-xs text-amber-700 dark:text-amber-400 pl-6 list-disc">
              {missingFields.map((field, idx) => (
                <li key={idx} className="font-medium">
                  {field}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Checklist Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {items.map((item, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border flex items-start gap-3 transition-colors ${
                item.isCompleted
                  ? 'border-emerald-200/60 dark:border-emerald-950/60 bg-emerald-50/30 dark:bg-emerald-950/10'
                  : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {item.isCompleted ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-slate-400 dark:text-slate-600" />
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className={`text-xs font-bold ${
                    item.isCompleted ? 'text-slate-900 dark:text-white' : 'text-slate-700 dark:text-slate-300'
                  }`}>
                    {item.label}
                  </span>
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0 uppercase">
                    {item.category}
                  </Badge>
                </div>
                {item.details && (
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                    {item.details}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {onNavigateToStep && !isReady && (
          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={() => onNavigateToStep(2)}
              className="text-xs text-blue-600 dark:text-blue-400 font-semibold hover:underline inline-flex items-center gap-1"
            >
              <span>Address missing items in Questions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
