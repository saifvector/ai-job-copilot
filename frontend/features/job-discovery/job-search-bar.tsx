'use client';

import React, { useState } from 'react';
import { Search, X, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface JobSearchBarProps {
  initialQuery?: string;
  onSearch: (query: string) => void;
  loading?: boolean;
}

const QUICK_ROLES = ['Full Stack', 'Backend Python', 'Next.js', 'AI Engineer', 'DevOps'];

export function JobSearchBar({ initialQuery = '', onSearch, loading = false }: JobSearchBarProps) {
  const [searchTerm, setSearchTerm] = useState(initialQuery);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchTerm);
  };

  const handleClear = () => {
    setSearchTerm('');
    onSearch('');
  };

  const handleQuickRole = (role: string) => {
    setSearchTerm(role);
    onSearch(role);
  };

  return (
    <div className="w-full space-y-3">
      <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by job title, company, technology (e.g., Senior Python Engineer, Stripe, FastAPI)..."
            className="pl-10 pr-10 h-12 text-base rounded-xl border-border/70 focus-visible:ring-primary/40 shadow-sm"
          />
          {searchTerm && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-0.5 rounded-full transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="h-12 px-6 rounded-xl font-medium shadow-sm gap-2"
        >
          <Search className="h-4 w-4" />
          <span>Search</span>
        </Button>
      </form>

      {/* Quick Search Suggestions */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
        <span className="flex items-center gap-1 font-medium mr-1">
          <Sparkles className="h-3 w-3 text-primary" /> Popular:
        </span>
        {QUICK_ROLES.map((role) => (
          <button
            key={role}
            type="button"
            onClick={() => handleQuickRole(role)}
            className="rounded-full border border-border/60 bg-muted/30 px-2.5 py-1 text-xs hover:bg-muted/80 hover:border-primary/40 hover:text-primary transition-all"
          >
            {role}
          </button>
        ))}
      </div>
    </div>
  );
}
