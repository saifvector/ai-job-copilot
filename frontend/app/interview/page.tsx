'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  BrainCircuit,
  Sparkles,
  Play,
  Flame,
  ListFilter,
  Plus,
  RefreshCw,
  Award,
  Layers,
  Calendar,
  History,
  CheckCircle2,
} from 'lucide-react';
import { useInterviewStore } from '@/store';
import {
  InterviewAnalyticsHeader,
  QuestionCard,
  PracticeModal,
  GenerateQuestionsModal,
  CoachingRoadmap,
} from '@/features/interview';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { InterviewQuestion } from '@/types';

export default function InterviewDashboardPage() {
  const {
    questions,
    sessions,
    analytics,
    coaching,
    loading,
    generating,
    fetchQuestions,
    fetchAnalytics,
    fetchCoaching,
    fetchSessions,
  } = useInterviewStore();

  const [activeQuestion, setActiveQuestion] = useState<InterviewQuestion | null>(null);
  const [isPracticeModalOpen, setIsPracticeModalOpen] = useState(false);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);

  useEffect(() => {
    fetchQuestions();
    fetchAnalytics();
    fetchCoaching('Senior Full-Stack Engineer');
    fetchSessions();
  }, [fetchQuestions, fetchAnalytics, fetchCoaching, fetchSessions]);

  const handlePractice = (q: InterviewQuestion) => {
    setActiveQuestion(q);
    setIsPracticeModalOpen(true);
  };

  const handleRefresh = () => {
    fetchQuestions();
    fetchAnalytics();
    fetchCoaching();
    fetchSessions();
  };

  // Featured slice of recent or unanswered questions
  const featuredQuestions = questions.slice(0, 6);

  return (
    <div className="container mx-auto p-4 md:p-6 max-w-7xl space-y-6">
      {/* Top Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/60 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                  AI Interview Preparation Platform
                </h1>
                <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 text-xs">
                  Phase 11
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                Practice tailored HR, Technical, Behavioral, and System Design questions with real-time AI evaluation.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
            className="h-9 gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Link href="/interview/practice">
            <Button variant="outline" size="sm" className="h-9 gap-1.5 text-xs">
              <ListFilter className="w-3.5 h-3.5" />
              Practice Hub
            </Button>
          </Link>

          <Link href="/interview/mock">
            <Button variant="outline" size="sm" className="h-9 gap-1.5 text-xs bg-amber-500/5 text-amber-500 border-amber-500/30 hover:bg-amber-500/10">
              <Flame className="w-3.5 h-3.5" />
              Mock Simulation
            </Button>
          </Link>

          <Button
            size="sm"
            onClick={() => setIsGenerateModalOpen(true)}
            className="h-9 gap-1.5 text-xs font-semibold shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            Generate Questions
          </Button>
        </div>
      </div>

      {/* Analytics KPI Header */}
      <InterviewAnalyticsHeader
        analytics={analytics}
        coaching={coaching}
        loading={loading && !analytics}
      />

      {/* Main Content Tabs */}
      <Tabs defaultValue="practice" className="space-y-4">
        <TabsList className="bg-muted/60 p-1 border border-border/50">
          <TabsTrigger value="practice" className="gap-1.5 text-xs font-medium">
            <Play className="w-3.5 h-3.5" />
            Active Practice ({questions.length})
          </TabsTrigger>
          <TabsTrigger value="roadmap" className="gap-1.5 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            Coaching & Roadmap
          </TabsTrigger>
          <TabsTrigger value="history" className="gap-1.5 text-xs font-medium">
            <History className="w-3.5 h-3.5" />
            Mock Interview History ({sessions.length})
          </TabsTrigger>
        </TabsList>

        {/* Practice Tab */}
        <TabsContent value="practice" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-foreground">Featured Questions</h2>
              <p className="text-xs text-muted-foreground">
                Personalized questions generated from your resume and target roles.
              </p>
            </div>
            <Link
              href="/interview/practice"
              className="text-xs font-medium text-primary hover:underline flex items-center gap-1"
            >
              View all ({questions.length}) questions &rarr;
            </Link>
          </div>

          {questions.length === 0 && !loading ? (
            <Card className="p-8 text-center border-dashed border-border/80 bg-card/40 space-y-3">
              <div className="p-3 rounded-full bg-primary/10 text-primary w-fit mx-auto">
                <BrainCircuit className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-foreground">No Interview Questions Generated Yet</h3>
              <p className="text-xs text-muted-foreground max-w-md mx-auto">
                Generate tailored interview questions matching your background, machine learning / full-stack projects, and target role.
              </p>
              <Button
                onClick={() => setIsGenerateModalOpen(true)}
                className="gap-2 text-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                Generate First Question Pack
              </Button>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {featuredQuestions.map((q) => (
                <QuestionCard key={q.id} question={q} onPractice={handlePractice} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Roadmap Tab */}
        <TabsContent value="roadmap" className="space-y-4">
          <CoachingRoadmap coaching={coaching} loading={loading && !coaching} />
        </TabsContent>

        {/* Mock Interview History Tab */}
        <TabsContent value="history" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-foreground">Recorded Mock Interview Sessions</h2>
              <p className="text-xs text-muted-foreground">
                Track full-loop interview performance and feedback trajectories over time.
              </p>
            </div>
            <Link href="/interview/mock">
              <Button size="sm" className="h-8 gap-1 text-xs">
                <Flame className="w-3.5 h-3.5 text-amber-400" />
                Launch New Mock Interview
              </Button>
            </Link>
          </div>

          {sessions.length === 0 ? (
            <Card className="p-8 text-center border-dashed border-border/80 bg-card/40 space-y-3">
              <div className="p-3 rounded-full bg-amber-500/10 text-amber-500 w-fit mx-auto">
                <Flame className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-foreground">No Mock Interviews Completed Yet</h3>
              <p className="text-xs text-muted-foreground max-w-md mx-auto">
                Start a timed mock simulation to test yourself across technical, behavioral, and architecture questions under real interview conditions.
              </p>
              <Link href="/interview/mock">
                <Button size="sm" className="gap-2 text-xs">
                  <Play className="w-3.5 h-3.5" />
                  Start Mock Interview
                </Button>
              </Link>
            </Card>
          ) : (
            <div className="space-y-3">
              {sessions.map((session) => (
                <Card
                  key={session.id}
                  className="p-4 border-border/60 bg-card/70 backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-foreground">{session.role}</span>
                      <Badge variant="outline" className="text-[10px] text-muted-foreground">
                        {new Date(session.createdAt).toLocaleDateString()}
                      </Badge>
                    </div>
                    {session.feedback && (
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {typeof session.feedback === 'string'
                          ? session.feedback
                          : session.feedback.summary || 'Completed session.'}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    <div className="text-right">
                      <div className="text-xs text-muted-foreground">Session Score</div>
                      <div className="text-xl font-black text-emerald-500">
                        {Math.round(session.score)}%
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Practice Modal */}
      <PracticeModal
        question={activeQuestion}
        isOpen={isPracticeModalOpen}
        onClose={() => {
          setIsPracticeModalOpen(false);
          setActiveQuestion(null);
        }}
      />

      {/* Generate Questions Modal */}
      <GenerateQuestionsModal
        isOpen={isGenerateModalOpen}
        onClose={() => setIsGenerateModalOpen(false)}
        onSuccess={() => {
          fetchQuestions();
          fetchAnalytics();
        }}
      />
    </div>
  );
}
