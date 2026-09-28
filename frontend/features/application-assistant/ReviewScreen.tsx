'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ApplicationDraft } from '@/types';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileText,
  ExternalLink,
  Lock,
  ArrowLeft,
  Copy,
  Check,
} from 'lucide-react';

interface ReviewScreenProps {
  draft: ApplicationDraft | null;
  accuracyConfirmed: boolean;
  onConfirmAccuracyChange: (confirmed: boolean) => void;
  onSubmitDraft: () => Promise<void>;
  onBackToQuestions: () => void;
  isSubmitting?: boolean;
}

export const ReviewScreen: React.FC<ReviewScreenProps> = ({
  draft,
  accuracyConfirmed,
  onConfirmAccuracyChange,
  onSubmitDraft,
  onBackToQuestions,
  isSubmitting = false,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  if (!draft) return null;

  const job = draft.job;
  const questions = draft.questions || [];
  const isSubmitted = draft.status === 'SubmittedByUser';

  const copyAnswer = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="space-y-6 mb-8">
      {/* Review Banner */}
      <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
        <CardHeader className="p-5 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="outline" className="text-xs">
                  Review & Final Verification
                </Badge>
                {isSubmitted && (
                  <Badge variant="success">Completed & Verified</Badge>
                )}
              </div>
              <CardTitle className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                Candidate Application Review Screen
              </CardTitle>
              <CardDescription className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Inspect your prepared application answers before finalizing. System never bypasses human review.
              </CardDescription>
            </div>

            {job?.applyUrl && (
              <a
                href={job.applyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm shrink-0"
              >
                <span>Open Employer Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </CardHeader>

        <CardContent className="p-5 space-y-4">
          {/* Target Role & Selected Document Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800 text-xs">
            <div>
              <span className="text-slate-500 dark:text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
                Target Role & Employer
              </span>
              <p className="font-bold text-slate-900 dark:text-white text-sm mt-0.5">
                {job?.title || 'Target Position'} at {job?.company || 'Company'}
              </p>
              <p className="text-slate-500 dark:text-slate-400 mt-0.5">
                {job?.location || 'Remote'} {job?.salary ? `• ${job.salary}` : ''}
              </p>
            </div>

            <div>
              <span className="text-slate-500 dark:text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
                Attached Resume Document
              </span>
              <div className="flex items-center gap-2 mt-1">
                <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="font-semibold text-slate-900 dark:text-white">
                  {draft.selectedResumeId ? 'Tailored Resume A (High ATS Match)' : 'Original Master Resume'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Readiness Score: <strong>{Math.round(draft.readinessScore)}%</strong>
              </p>
            </div>
          </div>

          {/* Prepared Answers Summary */}
          <div>
            <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-3">
              Application Answers Ready for Copy / Form Pre-Fill
            </h4>
            <div className="space-y-3">
              {questions.map((q, idx) => {
                const answerText = q.userAnswer || q.generatedAnswer || 'No answer recorded.';

                return (
                  <div
                    key={q.id}
                    className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                        {idx + 1}. {q.question}
                      </span>
                      <button
                        type="button"
                        onClick={() => copyAnswer(answerText, idx)}
                        className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-blue-600 transition-colors"
                      >
                        {copiedIndex === idx ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                            <span className="text-emerald-600">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed bg-slate-50 dark:bg-slate-950/40 p-3 rounded-lg border border-slate-100 dark:border-slate-800/80">
                      {answerText}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Strict Human Confirmation Checkbox */}
          <div className="p-4 rounded-xl bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/50 space-y-3">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="accuracy-confirmation"
                checked={accuracyConfirmed}
                onChange={(e) => onConfirmAccuracyChange(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
              <label
                htmlFor="accuracy-confirmation"
                className="text-xs font-medium text-slate-800 dark:text-slate-200 leading-relaxed cursor-pointer select-none"
              >
                <strong>Human Verification & Truthfulness Mandate:</strong> I confirm that I have reviewed all generated responses, updated any subjective placeholders, and verified complete factual accuracy and truthfulness based on my authentic experience.
              </label>
            </div>

            <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 pl-7">
              <Lock className="w-3.5 h-3.5 text-slate-400" />
              <span>AI Job Copilot assists preparation. Final submission is always explicitly performed and verified by you.</span>
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button
              variant="outline"
              size="sm"
              onClick={onBackToQuestions}
              className="text-xs flex items-center gap-1.5 w-full sm:w-auto"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Edit Answers</span>
            </Button>

            <Button
              variant="default"
              size="sm"
              onClick={onSubmitDraft}
              disabled={!accuracyConfirmed || isSubmitting || isSubmitted}
              className={`text-xs flex items-center gap-1.5 w-full sm:w-auto ${
                accuracyConfirmed && !isSubmitted
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : ''
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>
                {isSubmitted
                  ? 'Application Completed by Candidate'
                  : isSubmitting
                  ? 'Recording Submission...'
                  : 'Confirm & Mark as Submitted by Candidate'}
              </span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
