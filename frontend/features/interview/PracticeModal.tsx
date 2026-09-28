'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Lightbulb,
  Award,
  ChevronDown,
  ChevronUp,
  Clock,
  Loader2,
} from 'lucide-react';
import { InterviewQuestion, AnswerEvaluation } from '@/types';
import { useInterviewStore } from '@/store';

interface PracticeModalProps {
  question: InterviewQuestion | null;
  isOpen: boolean;
  onClose: () => void;
}

export function PracticeModal({ question, isOpen, onClose }: PracticeModalProps) {
  const {
    timerSeconds,
    isTimerRunning,
    startTimer,
    pauseTimer,
    resetTimer,
    tickTimer,
    evaluateAnswer,
    evaluating,
  } = useInterviewStore();

  const [userAnswer, setUserAnswer] = useState('');
  const [showSample, setShowSample] = useState(false);
  const [activeFeedback, setActiveFeedback] = useState<AnswerEvaluation | null>(null);

  // Sync with question state when modal opens
  useEffect(() => {
    if (question && isOpen) {
      setUserAnswer(question.userAnswer || '');
      resetTimer();
      setShowSample(false);
      // Preload previous evaluation if question was already evaluated
      if (question.feedback) {
        try {
          const parsed =
            typeof question.feedback === 'string'
              ? JSON.parse(question.feedback)
              : question.feedback;
          setActiveFeedback({
            questionId: question.id,
            score: question.score ?? 75,
            strengths: parsed.strengths || ['Well articulated response.'],
            weaknesses: parsed.weaknesses || [],
            suggestedImprovements: parsed.suggestedImprovements || [],
            feedback: typeof question.feedback === 'string' ? question.feedback : 'Evaluated',
            evaluatedAt: question.evaluatedAt || new Date().toISOString(),
          });
        } catch {
          setActiveFeedback({
            questionId: question.id,
            score: question.score ?? 75,
            strengths: ['Practice recorded.'],
            weaknesses: [],
            suggestedImprovements: [],
            feedback: typeof question.feedback === 'string' ? question.feedback : 'Evaluated',
            evaluatedAt: question.evaluatedAt || new Date().toISOString(),
          });
        }
      } else {
        setActiveFeedback(null);
      }
    }
  }, [question, isOpen, resetTimer]);

  // Timer interval
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        tickTimer();
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isTimerRunning, tickTimer]);

  if (!question) return null;

  const formatTimer = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleEvaluate = async () => {
    if (!userAnswer.trim()) return;
    pauseTimer();
    const result = await evaluateAnswer({
      questionId: question.id,
      question: question.question,
      userAnswer,
      category: question.category,
      difficulty: question.difficulty,
    });
    if (result) {
      setActiveFeedback(result);
    }
  };

  const wordCount = userAnswer.trim() ? userAnswer.trim().split(/\s+/).length : 0;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 65) return 'text-blue-500';
    if (score >= 50) return 'text-amber-500';
    return 'text-rose-500';
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="full"
      title={
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-xs font-medium">
              {question.category}
            </Badge>
            <Badge variant="secondary" className="text-xs uppercase font-semibold">
              {question.difficulty}
            </Badge>
          </div>
          <div className="text-lg font-bold text-foreground leading-snug">
            {question.question}
          </div>
        </div>
      }
      description={question.explanation || undefined}
      footer={
        <Button variant="outline" onClick={onClose} className="w-full sm:w-auto text-xs">
          Done & Close Practice
        </Button>
      }
    >
      <div className="space-y-4 my-1">
        {/* Timer and Controls Bar */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border/50">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            <span className="font-mono text-lg font-bold text-foreground">
              {formatTimer(timerSeconds)}
            </span>
            <span className="text-xs text-muted-foreground hidden sm:inline">
              (target: 2-3 mins)
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            {!isTimerRunning ? (
              <Button
                size="sm"
                variant="outline"
                onClick={startTimer}
                className="h-8 gap-1 text-xs"
              >
                <Play className="w-3.5 h-3.5 text-emerald-500" />
                Start Timer
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={pauseTimer}
                className="h-8 gap-1 text-xs"
              >
                <Pause className="w-3.5 h-3.5 text-amber-500" />
                Pause
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={resetTimer}
              className="h-8 px-2 text-xs text-muted-foreground"
              title="Reset Timer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>

        {/* User Answer Textarea */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs text-muted-foreground px-1">
            <label className="font-medium text-foreground">Your Spoken or Written Answer</label>
            <span>{wordCount} words</span>
          </div>
          <Textarea
            placeholder="Structure your answer clearly. For behavioral questions, consider the STAR format (Situation, Task, Action, Result). For technical questions, explain trade-offs and complexity..."
            value={userAnswer}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setUserAnswer(e.target.value)}
            className="min-h-[140px] text-sm leading-relaxed resize-y bg-background/50 focus:bg-background"
          />
        </div>

        {/* Action Row */}
        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setShowSample(!showSample)}
            className="flex items-center gap-1 text-xs font-medium text-primary hover:underline"
          >
            {showSample ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            {showSample ? 'Hide Model Reference Answer' : 'Peek Model Reference Answer'}
          </button>

          <Button
            onClick={handleEvaluate}
            disabled={evaluating || !userAnswer.trim()}
            className="gap-2 font-medium text-xs"
          >
            {evaluating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Evaluating with AI...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Evaluate Answer
              </>
            )}
          </Button>
        </div>

        {/* Sample Answer Box */}
        {showSample && question.sampleAnswer && (
          <Card className="p-3 bg-muted/40 border-primary/20 text-xs text-muted-foreground space-y-1">
            <span className="font-semibold text-foreground block text-[11px] uppercase tracking-wider text-primary">
              Model Reference Answer
            </span>
            <p className="whitespace-pre-line leading-relaxed">{question.sampleAnswer}</p>
          </Card>
        )}

        {/* AI Feedback & Evaluation Results */}
        {activeFeedback && (
          <Card className="p-4 border-border/80 bg-background/80 backdrop-blur space-y-3.5">
            <div className="flex items-center justify-between border-b border-border/60 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-md bg-primary/10 text-primary">
                  <Award className="w-4 h-4" />
                </div>
                <div>
                  <h5 className="text-sm font-bold text-foreground">AI Evaluation Result</h5>
                  <p className="text-[11px] text-muted-foreground">Calibrated on content & structure</p>
                </div>
              </div>

              <div className="flex items-baseline gap-1.5">
                <span className={`text-2xl font-extrabold ${getScoreColor(activeFeedback.score)}`}>
                  {activeFeedback.score}%
                </span>
                <span className="text-xs text-muted-foreground">score</span>
              </div>
            </div>

            {/* Strengths */}
            {activeFeedback.strengths && activeFeedback.strengths.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Strengths
                </span>
                <ul className="text-xs text-muted-foreground space-y-1 pl-5 list-disc">
                  {activeFeedback.strengths.map((item, idx) => (
                    <li key={idx} className="leading-snug">{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {activeFeedback.weaknesses && activeFeedback.weaknesses.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5" /> Gaps & Weaknesses
                </span>
                <ul className="text-xs text-muted-foreground space-y-1 pl-5 list-disc">
                  {activeFeedback.weaknesses.map((item, idx) => (
                    <li key={idx} className="leading-snug">{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggested Improvements */}
            {activeFeedback.suggestedImprovements && activeFeedback.suggestedImprovements.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <span className="text-xs font-semibold text-primary flex items-center gap-1.5">
                  <Lightbulb className="w-3.5 h-3.5" /> Recommended Improvements
                </span>
                <ul className="text-xs text-muted-foreground space-y-1 pl-5 list-disc">
                  {activeFeedback.suggestedImprovements.map((item, idx) => (
                    <li key={idx} className="leading-snug">{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        )}
      </div>
    </Modal>
  );
}
