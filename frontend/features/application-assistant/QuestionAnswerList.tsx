'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { ApplicationQuestion, AnswerType } from '@/types';
import {
  Sparkles,
  Copy,
  Check,
  CheckCircle,
  HelpCircle,
  AlertTriangle,
  RotateCw,
  Plus,
} from 'lucide-react';

interface QuestionAnswerListProps {
  questions: ApplicationQuestion[];
  answers: Record<string, string>;
  onUpdateAnswer: (questionId: string, answer: string, isReviewed?: boolean) => void;
  onRegenerateAnswers: () => void;
  isGenerating?: boolean;
}

export const QuestionAnswerList: React.FC<QuestionAnswerListProps> = ({
  questions,
  answers,
  onUpdateAnswer,
  onRegenerateAnswers,
  isGenerating = false,
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('ALL');

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredQuestions = filterType === 'ALL'
    ? questions
    : questions.filter((q) => q.answerType === filterType);

  const getAnswerTypeBadge = (type: AnswerType) => {
    switch (type) {
      case 'YesNo':
        return <Badge variant="secondary" className="text-[10px]">Yes / No</Badge>;
      case 'MultiSelect':
        return <Badge variant="secondary" className="text-[10px]">Multi-Select</Badge>;
      case 'Numeric':
        return <Badge variant="secondary" className="text-[10px]">Numeric</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px]">Free Text</Badge>;
    }
  };

  return (
    <div className="space-y-4 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            Application Questions & AI Responses
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Strictly grounded in your verified experience. Review and edit answers before submitting.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRegenerateAnswers}
            disabled={isGenerating}
            className="text-xs flex items-center gap-1.5"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin' : ''}`} />
            <span>{isGenerating ? 'Synthesizing...' : 'Regenerate Responses'}</span>
          </Button>
        </div>
      </div>

      {filteredQuestions.length === 0 ? (
        <Card className="border border-slate-200 dark:border-slate-800 p-8 text-center bg-white dark:bg-slate-900/60">
          <HelpCircle className="w-8 h-8 mx-auto text-slate-400 opacity-60 mb-2" />
          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
            No questions available for this draft.
          </p>
        </Card>
      ) : (
        filteredQuestions.map((q, idx) => {
          const currentVal = answers[q.id] !== undefined ? answers[q.id] : (q.userAnswer || q.generatedAnswer || '');
          const hasPlaceholder = currentVal.includes('[Candidate Input Required:') || currentVal.includes('[Candidate Note:');
          const isReviewed = q.isReviewed;

          return (
            <Card
              key={q.id}
              className={`border transition-all ${
                isReviewed
                  ? 'border-emerald-200 dark:border-emerald-900/40 bg-white dark:bg-slate-900/80 shadow-sm'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm'
              }`}
            >
              <CardHeader className="p-4 pb-2 border-b border-slate-100 dark:border-slate-800/80">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2.5">
                    <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="text-sm font-bold text-slate-900 dark:text-white">
                          {q.question}
                        </span>
                        {q.isRequired && (
                          <span className="text-[10px] font-semibold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/60 px-1.5 py-0.5 rounded">
                            Required
                          </span>
                        )}
                        {getAnswerTypeBadge(q.answerType)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <Button
                      variant={isReviewed ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => onUpdateAnswer(q.id, currentVal, !isReviewed)}
                      className={`h-7 px-2.5 text-xs flex items-center gap-1 ${
                        isReviewed
                          ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                      }`}
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>{isReviewed ? 'Reviewed' : 'Mark Reviewed'}</span>
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopy(q.id, currentVal)}
                      className="h-7 px-2 text-xs text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                      title="Copy response to clipboard"
                    >
                      {copiedId === q.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-4 pt-3 space-y-2">
                {/* Placeholder Warning */}
                {hasPlaceholder && (
                  <div className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 text-xs text-amber-800 dark:text-amber-300 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                    <span>
                      <strong>Candidate Input Required:</strong> Please replace the bracketed placeholder with your specific preferred value before submitting.
                    </span>
                  </div>
                )}

                {/* Adaptive Input by AnswerType */}
                {q.answerType === 'YesNo' ? (
                  <div className="flex items-center gap-3 pt-1">
                    <button
                      type="button"
                      onClick={() => onUpdateAnswer(q.id, 'Yes', true)}
                      className={`px-5 py-2 rounded-lg text-sm font-semibold border transition-all ${
                        currentVal.toLowerCase() === 'yes'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:border-slate-400'
                      }`}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => onUpdateAnswer(q.id, 'No', true)}
                      className={`px-5 py-2 rounded-lg text-sm font-semibold border transition-all ${
                        currentVal.toLowerCase() === 'no'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:border-slate-400'
                      }`}
                    >
                      No
                    </button>
                    <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">
                      Selected: <strong>{currentVal || 'Unselected'}</strong>
                    </span>
                  </div>
                ) : q.answerType === 'Numeric' ? (
                  <div className="flex items-center gap-3 max-w-xs pt-1">
                    <Input
                      type="number"
                      value={currentVal}
                      onChange={(e) => onUpdateAnswer(q.id, e.target.value, false)}
                      placeholder="e.g. 5"
                      className="text-sm font-medium"
                    />
                    <span className="text-xs text-slate-500 dark:text-slate-400 shrink-0">
                      years of experience
                    </span>
                  </div>
                ) : q.answerType === 'MultiSelect' && q.options && q.options.length > 0 ? (
                  <div className="space-y-2 pt-1">
                    <div className="flex flex-wrap gap-2">
                      {q.options.map((opt, optIdx) => {
                        const selectedList = currentVal ? currentVal.split(',').map((s) => s.trim().toLowerCase()) : [];
                        const isOptSelected = selectedList.includes(opt.toLowerCase());

                        return (
                          <button
                            key={optIdx}
                            type="button"
                            onClick={() => {
                              let nextList: string[];
                              const rawCurrent = currentVal ? currentVal.split(',').map((s) => s.trim()).filter(Boolean) : [];
                              if (isOptSelected) {
                                nextList = rawCurrent.filter((s) => s.toLowerCase() !== opt.toLowerCase());
                              } else {
                                nextList = [...rawCurrent, opt];
                              }
                              onUpdateAnswer(q.id, nextList.join(', '), true);
                            }}
                            className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-all ${
                              isOptSelected
                                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                : 'bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                            }`}
                          >
                            {opt}
                          </button>
                        );
                      })}
                    </div>
                    <Input
                      value={currentVal}
                      onChange={(e) => onUpdateAnswer(q.id, e.target.value, false)}
                      placeholder="Custom selection..."
                      className="text-xs mt-1"
                    />
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    <Textarea
                      value={currentVal}
                      onChange={(e) => onUpdateAnswer(q.id, e.target.value, false)}
                      rows={currentVal.length > 180 ? 4 : 2}
                      className="text-xs font-normal leading-relaxed resize-y"
                      placeholder="Enter or edit truthful answer..."
                    />
                    <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 px-1">
                      <span className="flex items-center gap-1 text-purple-600 dark:text-purple-400 font-medium">
                        <Sparkles className="w-3 h-3" />
                        AI synthesized with Gemini 2.5 Pro (Grounded in Resume)
                      </span>
                      <span>{currentVal.length} characters</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })
      )}
    </div>
  );
};
