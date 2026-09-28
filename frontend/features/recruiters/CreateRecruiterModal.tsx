'use client';

import React, { useState } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CreateRecruiterPayload } from '@/types';
import { UserPlus, Building2, Briefcase, Mail, Linkedin, FileText, AlertCircle } from 'lucide-react';

interface CreateRecruiterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CreateRecruiterPayload) => Promise<unknown>;
  loading?: boolean;
}

export function CreateRecruiterModal({
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}: CreateRecruiterModalProps) {
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [title, setTitle] = useState('');
  const [email, setEmail] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [notes, setNotes] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setFormError('Recruiter name is required.');
      return;
    }
    if (!company.trim()) {
      setFormError('Company name is required.');
      return;
    }

    setFormError(null);
    const success = await onSubmit({
      name: name.trim(),
      company: company.trim(),
      title: title.trim() || undefined,
      email: email.trim() || undefined,
      linkedinUrl: linkedinUrl.trim() || undefined,
      notes: notes.trim() || undefined,
    });

    if (success) {
      setName('');
      setCompany('');
      setTitle('');
      setEmail('');
      setLinkedinUrl('');
      setNotes('');
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="md"
      className="max-w-lg bg-card border-border"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Header */}
        <div className="flex items-center gap-2.5 pb-2 border-b border-border/60">
          <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20">
            <UserPlus className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-foreground">
              Add Recruiter or Contact
            </h2>
            <p className="text-xs text-muted-foreground">
              Track talent partners, hiring managers, and referral contacts in your CRM.
            </p>
          </div>
        </div>

        {formError && (
          <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{formError}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              Full Name <span className="text-rose-500">*</span>
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Sarah Jenkins"
              required
              className="text-xs h-9 bg-background/50 border-border/70"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              Company <span className="text-rose-500">*</span>
            </label>
            <Input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Stripe, OpenAI"
              required
              className="text-xs h-9 bg-background/50 border-border/70"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">
            Job Title / Role
          </label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Staff Technical Recruiter / Engineering Manager"
            className="text-xs h-9 bg-background/50 border-border/70"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              Email Address
            </label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="text-xs h-9 bg-background/50 border-border/70"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              LinkedIn Profile
            </label>
            <Input
              value={linkedinUrl}
              onChange={(e) => setLinkedinUrl(e.target.value)}
              placeholder="https://linkedin.com/in/..."
              className="text-xs h-9 bg-background/50 border-border/70"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">
            Private Notes & Context
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="How you met, specific team openings, mutual connections, or alignment notes..."
            className="w-full text-xs rounded-md border border-border/70 bg-background/50 p-2.5 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/60">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onClose}
            disabled={loading}
            className="text-xs h-8"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={loading}
            className="text-xs h-8 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
          >
            {loading ? 'Adding...' : 'Add to Network'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
