'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Flame,
  ArrowLeft,
  Clock,
  Play,
  Pause,
  CheckCircle2,
  AlertCircle,
  Award,
  Sparkles,
  ChevronRight,
  RotateCcw,
  Loader2,
  BookOpen,
} from 'lucide-react';
import { useInterviewStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { InterviewQuestion, MockInterviewSession } from '@/types';

type MockStep = 'setup' | 'session' | 'summary';

export default function MockInterviewPage() {
  const {
    questions,
    fetchQuestions,
    submitMockInterview,
    loading,
  } = useInterviewStore();

  const [step, setStep] = useState<MockStep>('setup');
  const [role, setRole] = useState('Senior Full-Stack Engineer');
  const [sessionQuestions, setSessionQuestions] = useState<InterviewQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [completedSession, setCompletedSession] = useState<MockInterviewSession | null>(null);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  // Timer effect during session
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isTimerActive && step === 'session') {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isTimerActive, step]);

  const formatTimer = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartSession = () => {
    // Pick 4-5 balanced questions (technical, behavioral, architecture, project)
    const pool = questions.length > 0 ? questions : [];
    const selected = pool.slice(0, 5);

    if (selected.length === 0) {
      // Fallback questions if none exist
      const fallbackQuestions: InterviewQuestion[] = [
        {
          id: 'mock-1',
          preparationId: 'mock-prep',
          category: 'Behavioral',
          difficulty: 'Medium',
          question: 'Describe a significant engineering challenge you faced and how you overcame it using the STAR method.',
          sampleAnswer: 'In my previous project, we encountered severe latency in database queries. I initiated profiling, identified missing composite indexes, and implemented Redis caching, reducing p99 latency by 72%.',
          explanation: 'Evaluates structured problem-solving and communication.',
          isCompleted: false,
          createdAt: new Date().toISOString(),
        },
        {
          id: 'mock-2',
          preparationId: 'mock-prep',
          category: 'Technical',
          difficulty: 'Hard',
          question: 'Explain the difference between process concurrency and thread parallelism in Python. When would you choose asyncio over multiprocessing?',
          sampleAnswer: 'Python has a GIL that prevents multiple native threads from executing Python bytecodes simultaneously. For I/O bound tasks, asyncio or threading is ideal. For CPU bound tasks, multiprocessing is required.',
          explanation: 'Tests Python internals and runtime execution understanding.',
          isCompleted: false,
          createdAt: new Date().toISOString(),
        },
        {
          id: 'mock-3',
          preparationId: 'mock-prep',
          category: 'System Design',
          difficulty: 'Hard',
          question: 'Design a distributed rate limiter that handles 100,000 requests per second across multiple regions with token bucket algorithm.',
          sampleAnswer: 'I would use Redis with Lua scripts to ensure atomic token decrement, deployed regionally with local caching or sliding window rate limiting.',
          explanation: 'Evaluates high-scale distributed systems and resilience.',
          isCompleted: false,
          createdAt: new Date().toISOString(),
        },
        {
          id: 'mock-4',
          preparationId: 'mock-prep',
          category: 'Project-Based',
          difficulty: 'Medium',
          question: 'In your machine learning / computer vision projects (e.g. Brain Tumor Detection), why did you choose U-Net architecture and what evaluation metrics did you optimize?',
          sampleAnswer: 'U-Net provides skip connections connecting contracting and expansive paths, preserving spatial detail crucial for segmenting small tumor boundaries. We optimized Dice Coefficient and IoU.',
          explanation: 'Probes resume claims and architecture rationale.',
          isCompleted: false,
          createdAt: new Date().toISOString(),
        },
      ];
      setSessionQuestions(fallbackQuestions);
    } else {
      setSessionQuestions(selected);
    }

    setCurrentIndex(0);
    setAnswers({});
    setTimerSeconds(0);
    setIsTimerActive(true);
    setStep('session');
  };

  const handleAnswerChange = (val: string) => {
    const qId = sessionQuestions[currentIndex]?.id;
    if (qId) {
      setAnswers((prev) => ({ ...prev, [qId]: val }));
    }
  };

  const handleNext = () => {
    if (currentIndex < sessionQuestions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleFinishMock = async () => {
    setIsTimerActive(false);
    setIsSubmitting(true);

    const qList = sessionQuestions.map((q) => ({
      questionId: q.id,
      question: q.question,
      category: q.category,
      difficulty: q.difficulty,
      userAnswer: answers[q.id] || 'No answer provided.',
    }));

    const result = await submitMockInterview({
      role,
      answers: qList,
    });

    setIsSubmitting(false);
    if (result) {
      setCompletedSession(result);
      setStep('summary');
    }
  };

  const currentQ = sessionQuestions[currentIndex];
  const progressPct = sessionQuestions.length > 0
    ? Math.round(((currentIndex + 1) / sessionQuestions.length) * 100)
    : 0;

  return (
    <div className="container mx-auto p-4 md:p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/60 pb-4">
        <div>
          <Link
            href="/interview"
            className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 mb-1 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Interview Dashboard
          </Link>
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-amber-500" />
            <h1 className="text-xl font-bold tracking-tight text-foreground">
              Mock Interview Simulation
            </h1>
          </div>
        </div>

        {step === 'session' && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-card border border-border/60 shadow-xs">
              <Clock className="w-4 h-4 text-primary" />
              <span className="font-mono text-base font-bold text-foreground">
                {formatTimer(timerSeconds)}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsTimerActive(!isTimerActive)}
              className="h-8 text-xs"
            >
              {isTimerActive ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            </Button>
          </div>
        )}
      </div>

      {/* STEP 1: SETUP */}
      {step === 'setup' && (
        <Card className="p-6 border-border/70 bg-card/70 backdrop-blur-sm space-y-6">
          <div className="space-y-2">
            <Badge variant="outline" className="bg-amber-500/10 text-amber-500 border-amber-500/30 text-xs">
              Timed Simulation Mode
            </Badge>
            <h2 className="text-xl font-bold text-foreground">
              Ready for your simulated technical & behavioral loop?
            </h2>
            <p className="text-xs text-muted-foreground leading-relaxed">
              This mock interview simulates a real 4-to-5 question engineering interview round. You will be evaluated on technical accuracy, structure, the STAR framework, and clear problem-solving communication.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3.5 rounded-lg bg-muted/40 border border-border/50 text-xs space-y-1">
              <div className="font-semibold text-foreground flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-primary" /> Timed Conditions
              </div>
              <p className="text-muted-foreground">Keep pace with a live timer simulating 2-3 mins per question.</p>
            </div>
            <div className="p-3.5 rounded-lg bg-muted/40 border border-border/50 text-xs space-y-1">
              <div className="font-semibold text-foreground flex items-center gap-1">
                <Award className="w-3.5 h-3.5 text-primary" /> Calibrated Scoring
              </div>
              <p className="text-muted-foreground">Receive an aggregate 0-100 benchmark score calibrated on role seniority.</p>
            </div>
            <div className="p-3.5 rounded-lg bg-muted/40 border border-border/50 text-xs space-y-1">
              <div className="font-semibold text-foreground flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-primary" /> Full Feedback
              </div>
              <p className="text-muted-foreground">Get comprehensive strengths, weaknesses, and key improvement items.</p>
            </div>
          </div>

          <div className="space-y-1.5 max-w-md">
            <label className="text-xs font-semibold text-foreground">Target Role</label>
            <input
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full h-9 px-3 rounded-md bg-background border border-border text-sm"
              placeholder="e.g. Senior Full-Stack Engineer"
            />
          </div>

          <div className="pt-2 flex items-center justify-between border-t border-border/40">
            <span className="text-xs text-muted-foreground">
              {questions.length > 0
                ? `${Math.min(5, questions.length)} curated questions ready`
                : 'Default 4-question comprehensive simulation ready'}
            </span>
            <Button onClick={handleStartSession} className="gap-2 font-semibold">
              <Play className="w-4 h-4" /> Start Mock Interview
            </Button>
          </div>
        </Card>
      )}

      {/* STEP 2: ACTIVE SESSION */}
      {step === 'session' && currentQ && (
        <div className="space-y-4">
          {/* Progress bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>
                Question <strong className="text-foreground">{currentIndex + 1}</strong> of{' '}
                {sessionQuestions.length}
              </span>
              <span>{progressPct}% Completed</span>
            </div>
            <Progress value={progressPct} className="h-1.5" />
          </div>

          {/* Current Question Card */}
          <Card className="p-6 border-border/80 bg-card/80 backdrop-blur-sm space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs font-medium">
                {currentQ.category}
              </Badge>
              <Badge variant="secondary" className="text-xs uppercase font-semibold">
                {currentQ.difficulty}
              </Badge>
            </div>

            <h3 className="text-lg font-bold text-foreground leading-snug">
              {currentQ.question}
            </h3>

            {currentQ.explanation && (
              <p className="text-xs text-muted-foreground">
                {currentQ.explanation}
              </p>
            )}

            {/* Answer Field */}
            <div className="space-y-1.5 pt-2">
              <label className="text-xs font-semibold text-foreground">Your Response</label>
              <Textarea
                placeholder="Type your response as you would speak it to an interviewer..."
                value={answers[currentQ.id] || ''}
                onChange={(e) => handleAnswerChange(e.target.value)}
                className="min-h-[180px] text-sm leading-relaxed resize-y bg-background/50 focus:bg-background"
              />
            </div>

            {/* Navigation buttons */}
            <div className="flex items-center justify-between pt-3 border-t border-border/40">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrevious}
                disabled={currentIndex === 0}
                className="text-xs"
              >
                Previous Question
              </Button>

              {currentIndex < sessionQuestions.length - 1 ? (
                <Button size="sm" onClick={handleNext} className="gap-1 text-xs font-medium">
                  Next Question <ChevronRight className="w-3.5 h-3.5" />
                </Button>
              ) : (
                <Button
                  size="sm"
                  onClick={handleFinishMock}
                  disabled={isSubmitting}
                  className="gap-2 font-semibold bg-emerald-600 hover:bg-emerald-700 text-white text-xs"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Evaluating Session...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Submit & Score Interview
                    </>
                  )}
                </Button>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* STEP 3: SUMMARY & SCORE REPORT */}
      {step === 'summary' && completedSession && (
        <Card className="p-6 border-border/80 bg-card/80 backdrop-blur-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-5">
            <div>
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-xs mb-1">
                Session Completed
              </Badge>
              <h2 className="text-xl font-bold text-foreground">
                Mock Interview Performance Report
              </h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                Target Role: <strong>{completedSession.role}</strong> &bull; Total Time: {formatTimer(timerSeconds)}
              </p>
            </div>

            <div className="flex items-center gap-3 bg-muted/40 p-3 rounded-xl border border-border/50 shrink-0">
              <div className="p-2 rounded-lg bg-primary/10 text-primary">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground block">Session Score</span>
                <span className="text-3xl font-black text-emerald-500">
                  {Math.round(completedSession.score)}%
                </span>
              </div>
            </div>
          </div>

          {/* AI Comprehensive Feedback */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-primary" /> Evaluator Assessment
            </h3>
            <div className="p-4 rounded-lg bg-background/60 border border-border/60 text-xs text-muted-foreground whitespace-pre-line leading-relaxed">
              {typeof completedSession.feedback === 'string'
                ? completedSession.feedback
                : completedSession.feedback?.summary || 'Completed mock interview evaluation.'}
            </div>

            {typeof completedSession.feedback !== 'string' &&
              completedSession.feedback?.questionBreakdown &&
              completedSession.feedback.questionBreakdown.length > 0 && (
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">
                    Question-by-Question Breakdown
                  </h4>
                  <div className="grid grid-cols-1 gap-2.5">
                    {completedSession.feedback.questionBreakdown.map((item: any, idx: number) => (
                      <Card key={idx} className="p-3 border-border/50 bg-muted/20 text-xs space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-foreground">{item.question}</span>
                          <span className="font-bold text-emerald-500">{item.score}%</span>
                        </div>
                        {item.strengths && item.strengths.length > 0 && (
                          <p className="text-[11px] text-emerald-400">
                            <strong>Strength:</strong> {item.strengths.join(', ')}
                          </p>
                        )}
                        {item.improvements && item.improvements.length > 0 && (
                          <p className="text-[11px] text-amber-400">
                            <strong>Improvement:</strong> {item.improvements.join(', ')}
                          </p>
                        )}
                      </Card>
                    ))}
                  </div>
                </div>
              )}
          </div>

          <div className="pt-2 flex items-center justify-between border-t border-border/40">
            <Link href="/interview">
              <Button variant="outline" size="sm" className="text-xs">
                Back to Dashboard
              </Button>
            </Link>

            <Button
              size="sm"
              onClick={() => {
                setStep('setup');
                setCompletedSession(null);
              }}
              className="gap-1.5 text-xs font-medium"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Retake Simulation
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
