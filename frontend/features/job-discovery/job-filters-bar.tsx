'use client';

import React from 'react';
import { Filter, RotateCcw, MapPin, DollarSign, Layers, ArrowUpDown, Briefcase } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { JobFilters } from '@/types';

interface JobFiltersBarProps {
  filters: JobFilters;
  onChange: (filters: Partial<JobFilters>) => void;
  onReset: () => void;
  loading?: boolean;
}

const SOURCE_OPTIONS = [
  { value: '', label: 'All Sources' },
  { value: 'RemoteOK', label: 'RemoteOK' },
  { value: 'Greenhouse', label: 'Greenhouse' },
  { value: 'Lever', label: 'Lever' },
  { value: 'Wellfound', label: 'Wellfound' },
];

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest Posted' },
  { value: 'highest_salary', label: 'Highest Salary' },
  { value: 'most_relevant', label: 'Most Relevant' },
];

export function JobFiltersBar({ filters, onChange, onReset, loading = false }: JobFiltersBarProps) {
  const hasActiveFilters = Boolean(
    filters.role ||
    filters.location ||
    filters.source ||
    filters.minSalary ||
    (filters.sortBy && filters.sortBy !== 'newest')
  );

  return (
    <div className="rounded-2xl border border-border/60 bg-card/60 backdrop-blur-md p-4 shadow-sm space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 pb-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <Filter className="h-4 w-4 text-primary" />
          <span>Filter & Refine</span>
        </div>

        {hasActiveFilters && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-8 text-xs text-muted-foreground hover:text-foreground gap-1.5"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset Filters</span>
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Role Filter */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <Briefcase className="h-3.5 w-3.5 text-primary" /> Role
          </label>
          <Input
            value={filters.role || ''}
            onChange={(e) => onChange({ role: e.target.value })}
            placeholder="e.g. Backend, Architect"
            className="h-9 text-xs rounded-lg"
          />
        </div>

        {/* Location Filter */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-primary" /> Location
          </label>
          <Input
            value={filters.location || ''}
            onChange={(e) => onChange({ location: e.target.value })}
            placeholder="e.g. Remote, San Francisco"
            className="h-9 text-xs rounded-lg"
          />
        </div>

        {/* Min Salary Filter */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <DollarSign className="h-3.5 w-3.5 text-primary" /> Min Salary ($/yr)
          </label>
          <Input
            type="number"
            min={0}
            step={10000}
            value={filters.minSalary || ''}
            onChange={(e) => onChange({ minSalary: e.target.value ? Number(e.target.value) : undefined })}
            placeholder="e.g. 120000"
            className="h-9 text-xs rounded-lg"
          />
        </div>

        {/* Source Filter */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-primary" /> Source
          </label>
          <Select
            options={SOURCE_OPTIONS}
            value={filters.source || ''}
            onChange={(e) => onChange({ source: e.target.value })}
            className="h-9 text-xs rounded-lg"
          />
        </div>

        {/* Sort By Filter */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <ArrowUpDown className="h-3.5 w-3.5 text-primary" /> Sort Order
          </label>
          <Select
            options={SORT_OPTIONS}
            value={filters.sortBy || 'newest'}
            onChange={(e) => onChange({ sortBy: e.target.value })}
            className="h-9 text-xs rounded-lg"
          />
        </div>

      </div>
    </div>
  );
}
