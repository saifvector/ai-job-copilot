'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { AssistantAnalytics } from '@/types';
import { FileEdit, CheckCircle2, Clock, Award, Sparkles } from 'lucide-react';

interface AssistantAnalyticsHeaderProps {
  analytics: AssistantAnalytics | null;
  currentScore?: number;
}

export const AssistantAnalyticsHeader: React.FC<AssistantAnalyticsHeaderProps> = ({
  analytics,
  currentScore = 0,
}) => {
  const draftsCreated = analytics?.draftsCreated ?? 0;
  const draftsCompleted = analytics?.draftsCompleted ?? 0;
  const avgTime = analytics?.averageCompletionTimeMinutes ?? 0;
  const totalAnswered = analytics?.totalQuestionsAnswered ?? 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:shadow transition-shadow">
        <CardContent className="p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Drafts Created
            </p>
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
              {draftsCreated}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Target job preparations
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/60 flex items-center justify-center text-blue-600 dark:text-blue-400">
            <FileEdit className="w-5 h-5" />
          </div>
        </CardContent>
      </Card>

      <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:shadow transition-shadow">
        <CardContent className="p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Drafts Completed
            </p>
            <h3 className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
              {draftsCompleted}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Verified & candidate-submitted
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </CardContent>
      </Card>

      <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:shadow transition-shadow">
        <CardContent className="p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Avg. Completion Time
            </p>
            <h3 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
              {avgTime > 0 ? `${avgTime} min` : '10 min'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              From draft to verified submission
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <Clock className="w-5 h-5" />
          </div>
        </CardContent>
      </Card>

      <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:shadow transition-shadow">
        <CardContent className="p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Active Readiness
            </p>
            <h3 className={`text-2xl font-bold mt-1 ${
              currentScore >= 80
                ? 'text-emerald-600 dark:text-emerald-400'
                : currentScore >= 50
                ? 'text-amber-500 dark:text-amber-400'
                : 'text-slate-700 dark:text-slate-300'
            }`}>
              {Math.round(currentScore)}%
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {currentScore >= 80 ? 'Ready for review' : 'Checklist pending'}
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950/60 flex items-center justify-center text-purple-600 dark:text-purple-400">
            <Award className="w-5 h-5" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
