'use client';

import React, { useState } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Sparkles, BrainCircuit, Loader2 } from 'lucide-react';
import { useInterviewStore } from '@/store';

interface GenerateQuestionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const PREPARATION_OPTIONS = [
  { label: 'Comprehensive (Balanced Mix)', value: 'Comprehensive' },
  { label: 'Technical Deep Dive', value: 'Technical' },
  { label: 'Behavioral (STAR Format)', value: 'Behavioral' },
  { label: 'System Design & Architecture', value: 'System Design' },
  { label: 'Resume & Project-Based', value: 'Project-Based' },
  { label: 'HR & Culture Fit', value: 'HR' },
];

export function GenerateQuestionsModal({
  isOpen,
  onClose,
  onSuccess,
}: GenerateQuestionsModalProps) {
  const { generateQuestions, generating } = useInterviewStore();

  const [role, setRole] = useState('Senior Full-Stack Engineer');
  const [prepType, setPrepType] = useState('Comprehensive');
  const [focusAreas, setFocusAreas] = useState('Python, React, System Design, AI/ML');
  const [count, setCount] = useState<number>(6);
  const [jobDescription, setJobDescription] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!role.trim()) return;

    const focusList = focusAreas
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    const result = await generateQuestions({
      role: role.trim(),
      preparationType: prepType,
      focusAreas: focusList.length > 0 ? focusList : undefined,
      questionCount: count,
      jobDescription: jobDescription.trim() || undefined,
    } as any);

    if (result) {
      if (onSuccess) onSuccess();
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2 text-primary">
          <BrainCircuit className="w-5 h-5" />
          <span className="text-lg font-bold text-foreground">
            Generate Interview Preparation
          </span>
        </div>
      }
      description="Personalized interview questions generated with Gemini 2.5 Pro based on your resume, target role, and projects."
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4 py-1">
        {/* Target Role */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">Target Role *</label>
          <Input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. Senior Full-Stack Engineer, Machine Learning Specialist"
            required
            className="text-sm"
          />
        </div>

        {/* Preparation Type */}
        <div className="space-y-1.5">
          <Select
            label="Interview Focus"
            value={prepType}
            onChange={(e) => setPrepType(e.target.value)}
            options={PREPARATION_OPTIONS}
          />
        </div>

        {/* Focus Areas */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">
            Skills / Technologies / Focus Topics
          </label>
          <Input
            value={focusAreas}
            onChange={(e) => setFocusAreas(e.target.value)}
            placeholder="e.g. Python, Microservices, U-Net, PyTorch, React"
            className="text-sm"
          />
          <p className="text-[11px] text-muted-foreground">
            Comma-separated topics you want specifically tested
          </p>
        </div>

        {/* Number of Questions */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">Question Pack Size</label>
          <div className="grid grid-cols-3 gap-2">
            {[4, 6, 10].map((num) => (
              <Button
                key={num}
                type="button"
                variant={count === num ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCount(num)}
                className="h-8 text-xs font-medium"
              >
                {num} Questions
              </Button>
            ))}
          </div>
        </div>

        {/* Optional Job Description */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">
            Target Job Description <span className="font-normal text-muted-foreground">(Optional)</span>
          </label>
          <Textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste specific JD requirements or leave blank to infer from resume..."
            className="min-h-[80px] text-xs resize-y"
          />
        </div>

        <div className="pt-3 flex items-center justify-end gap-2 border-t border-border/50">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={generating}
            className="text-xs"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={generating || !role.trim()}
            className="gap-2 font-medium text-xs"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating with Gemini 2.5...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Questions
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
