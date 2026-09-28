'use client';

import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import {
  ListFilter,
  Search,
  Plus,
  ArrowLeft,
  RefreshCw,
  BrainCircuit,
  SlidersHorizontal,
} from 'lucide-react';
import { useInterviewStore } from '@/store';
import {
  QuestionCard,
  PracticeModal,
  GenerateQuestionsModal,
} from '@/features/interview';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { InterviewQuestion } from '@/types';

export default function InterviewPracticePage() {
  const {
    questions,
    loading,
    fetchQuestions,
    selectedCategory,
    selectedDifficulty,
    searchQuery,
    setSelectedCategory,
    setSelectedDifficulty,
    setSearchQuery,
  } = useInterviewStore();

  const [activeQuestion, setActiveQuestion] = useState<InterviewQuestion | null>(null);
  const [isPracticeModalOpen, setIsPracticeModalOpen] = useState(false);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'unanswered'>('all');

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  const categories = [
    'All',
    'Technical',
    'Behavioral',
    'System Design',
    'Project-Based',
    'Resume-Based',
    'HR',
  ];

  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];

  const filteredQuestions = useMemo(() => {
    return questions.filter((q) => {
      // Category filter
      if (selectedCategory && selectedCategory !== 'All' && q.category !== selectedCategory) {
        return false;
      }
      // Difficulty filter
      if (selectedDifficulty && selectedDifficulty !== 'All' && q.difficulty.toLowerCase() !== selectedDifficulty.toLowerCase()) {
        return false;
      }
      // Status filter
      if (statusFilter === 'completed' && !q.isCompleted) return false;
      if (statusFilter === 'unanswered' && q.isCompleted) return false;

      // Keyword search
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesQuestion = q.question.toLowerCase().includes(query);
        const matchesExplanation = q.explanation ? q.explanation.toLowerCase().includes(query) : false;
        const matchesCategory = q.category.toLowerCase().includes(query);
        return matchesQuestion || matchesExplanation || matchesCategory;
      }

      return true;
    });
  }, [questions, selectedCategory, selectedDifficulty, statusFilter, searchQuery]);

  const handlePractice = (q: InterviewQuestion) => {
    setActiveQuestion(q);
    setIsPracticeModalOpen(true);
  };

  return (
    <div className="container mx-auto p-4 md:p-6 max-w-7xl space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/60 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link
              href="/interview"
              className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Interview Dashboard
            </Link>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
              <ListFilter className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-foreground">
                Question Practice Hub
              </h1>
              <p className="text-xs text-muted-foreground">
                Filter and practice specialized questions across Technical, Behavioral, Architecture, and Project domains.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchQuestions()}
            disabled={loading}
            className="h-9 gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Button
            size="sm"
            onClick={() => setIsGenerateModalOpen(true)}
            className="h-9 gap-1.5 text-xs font-semibold shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            Generate New Pack
          </Button>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="space-y-3 bg-card/60 p-4 rounded-xl border border-border/60 backdrop-blur-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search questions by topic, keyword, or framework..."
              className="pl-9 h-9 text-xs bg-background/50"
            />
          </div>

          {/* Difficulty & Status Selectors */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-1 bg-muted/60 p-1 rounded-lg border border-border/40 text-xs">
              <span className="text-[11px] font-semibold text-muted-foreground px-1.5">
                Difficulty:
              </span>
              {difficulties.map((diff) => (
                <button
                  key={diff}
                  onClick={() => setSelectedDifficulty(diff === 'All' ? null : diff)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    (selectedDifficulty === diff || (!selectedDifficulty && diff === 'All'))
                      ? 'bg-background text-foreground shadow-xs font-semibold'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {diff}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1 bg-muted/60 p-1 rounded-lg border border-border/40 text-xs">
              <span className="text-[11px] font-semibold text-muted-foreground px-1.5">
                Status:
              </span>
              {(['all', 'unanswered', 'completed'] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2 py-0.5 rounded text-[11px] capitalize transition-colors ${
                    statusFilter === st
                      ? 'bg-background text-foreground shadow-xs font-semibold'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Category Pill Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-1 pb-0.5 scrollbar-none">
          <span className="text-xs font-semibold text-muted-foreground mr-1 flex items-center gap-1">
            <SlidersHorizontal className="w-3 h-3" /> Category:
          </span>
          {categories.map((cat) => {
            const isSelected =
              (selectedCategory === cat) || (!selectedCategory && cat === 'All');
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat === 'All' ? null : cat)}
                className={`px-3 py-1 rounded-full text-xs font-medium shrink-0 transition-all ${
                  isSelected
                    ? 'bg-primary text-primary-foreground font-semibold shadow-xs'
                    : 'bg-muted/60 text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* Result Count */}
      <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
        <span>
          Showing <strong className="text-foreground">{filteredQuestions.length}</strong> of{' '}
          {questions.length} questions
        </span>
        {filteredQuestions.length > 0 && (
          <span>
            {filteredQuestions.filter((q) => q.isCompleted).length} completed in current view
          </span>
        )}
      </div>

      {/* Question Cards Grid */}
      {filteredQuestions.length === 0 ? (
        <Card className="p-8 text-center border-dashed border-border/80 bg-card/40 space-y-3">
          <div className="p-3 rounded-full bg-primary/10 text-primary w-fit mx-auto">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-foreground">No matching questions found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Try adjusting your search filters or generate fresh interview questions for your target role.
          </p>
          <Button
            onClick={() => setIsGenerateModalOpen(true)}
            size="sm"
            className="gap-2 text-xs"
          >
            <Plus className="w-3.5 h-3.5" />
            Generate Questions
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredQuestions.map((q) => (
            <QuestionCard key={q.id} question={q} onPractice={handlePractice} />
          ))}
        </div>
      )}

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
        onSuccess={() => fetchQuestions()}
      />
    </div>
  );
}
