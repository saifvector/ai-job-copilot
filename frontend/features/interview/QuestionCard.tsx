'use client';

import React, { useState } from 'react';
import {
  HelpCircle,
  Award,
  ChevronDown,
  ChevronUp,
  Play,
  CheckCircle2,
  Brain,
  Code2,
  Users2,
  Cpu,
  Layers,
  FileCheck,
} from 'lucide-react';
import { InterviewQuestion } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface QuestionCardProps {
  question: InterviewQuestion;
  onPractice: (question: InterviewQuestion) => void;
}

export function QuestionCard({ question, onPractice }: QuestionCardProps) {
  const [showSample, setShowSample] = useState(false);

  const getCategoryConfig = (category: string) => {
    switch (category) {
      case 'Technical':
        return {
          icon: Code2,
          color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
        };
      case 'Behavioral':
        return {
          icon: Users2,
          color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
        };
      case 'System Design':
        return {
          icon: Cpu,
          color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        };
      case 'Project-Based':
        return {
          icon: Layers,
          color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        };
      case 'Resume-Based':
        return {
          icon: FileCheck,
          color: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
        };
      case 'HR':
      default:
        return {
          icon: Brain,
          color: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        };
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'hard':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'easy':
      default:
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
  };

  const catConfig = getCategoryConfig(question.category);
  const CatIcon = catConfig.icon;

  return (
    <Card className="p-4 border-border/50 bg-card/60 backdrop-blur-sm hover:border-border transition-all flex flex-col justify-between group">
      <div>
        {/* Header with badges */}
        <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={`flex items-center gap-1 text-[11px] font-medium py-0.5 ${catConfig.color}`}
            >
              <CatIcon className="w-3 h-3" />
              {question.category}
            </Badge>
            <Badge
              variant="outline"
              className={`text-[10px] font-medium uppercase tracking-wider py-0.5 ${getDifficultyColor(
                question.difficulty
              )}`}
            >
              {question.difficulty}
            </Badge>
          </div>

          {/* Completion / Score status */}
          {question.isCompleted ? (
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{question.score !== undefined ? `${question.score}%` : 'Done'}</span>
            </div>
          ) : (
            <span className="text-[11px] text-muted-foreground">Unanswered</span>
          )}
        </div>

        {/* Question Prompt */}
        <h4 className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors leading-snug mb-2">
          {question.question}
        </h4>

        {/* Explanation / Context */}
        {question.explanation && (
          <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
            {question.explanation}
          </p>
        )}

        {/* Sample Answer Collapse */}
        {question.sampleAnswer && (
          <div className="mb-3">
            <button
              onClick={() => setShowSample(!showSample)}
              className="flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
            >
              {showSample ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {showSample ? 'Hide Model Sample Answer' : 'View Model Sample Answer'}
            </button>
            {showSample && (
              <div className="mt-2 p-2.5 rounded-md bg-muted/60 border border-border/60 text-xs text-muted-foreground whitespace-pre-line leading-relaxed">
                <span className="font-semibold text-foreground block mb-1 text-[11px]">
                  Sample Answer Strategy:
                </span>
                {question.sampleAnswer}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="pt-2 border-t border-border/40 flex items-center justify-between gap-2 mt-auto">
        <div className="text-[11px] text-muted-foreground">
          {question.userAnswer ? (
            <span className="text-primary font-medium">Answer Drafted</span>
          ) : (
            <span>Ready for response</span>
          )}
        </div>

        <Button
          size="sm"
          onClick={() => onPractice(question)}
          className="h-8 gap-1.5 text-xs font-medium"
          variant={question.isCompleted ? 'outline' : 'default'}
        >
          <Play className="w-3 h-3" />
          {question.isCompleted ? 'Practice Again' : 'Practice Answer'}
        </Button>
      </div>
    </Card>
  );
}
