'use client';

import * as React from 'react';
import { Sparkles, Search, MapPin, Building, Briefcase, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { useMatchingStore } from '@/store/matching-store';

export function MatchFiltersBar() {
  const { filters, setFilters, resetFilters, runMatching, runningMatch } = useMatchingStore();

  const [roleInput, setRoleInput] = React.useState(filters.role || '');
  const [locationInput, setLocationInput] = React.useState(filters.location || '');
  const [companyInput, setCompanyInput] = React.useState(filters.company || '');

  // Keep local inputs in sync if store filters reset
  React.useEffect(() => {
    setRoleInput(filters.role || '');
    setLocationInput(filters.location || '');
    setCompanyInput(filters.company || '');
  }, [filters.role, filters.location, filters.company]);

  const handleScoreChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setFilters({ minScore: val === 'all' ? null : parseFloat(val) });
  };

  const handleApplyTextFilters = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({
      role: roleInput.trim() || undefined,
      location: locationInput.trim() || undefined,
      company: companyInput.trim() || undefined,
    });
  };

  const handleReset = () => {
    setRoleInput('');
    setLocationInput('');
    setCompanyInput('');
    resetFilters();
  };

  const hasActiveFilters = Boolean(
    filters.minScore || filters.role || filters.location || filters.company
  );

  return (
    <div className="space-y-3 rounded-xl border border-border/70 bg-card/40 p-4 shadow-sm backdrop-blur-sm">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <form onSubmit={handleApplyTextFilters} className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-4 flex-1">
          {/* Match Score Filter */}
          <div>
            <label className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground mb-1 block">
              Match Fit Threshold
            </label>
            <Select
              value={filters.minScore ? filters.minScore.toString() : 'all'}
              onChange={handleScoreChange}
              className="h-9 text-xs"
            >
              <option value="all">All Match Scores</option>
              <option value="90">90%+ Excellent Fit</option>
              <option value="75">75%+ Strong Fit</option>
              <option value="60">60%+ Moderate Fit</option>
            </Select>
          </div>

          {/* Role Filter */}
          <div>
            <label className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground mb-1 block">
              Role or Title
            </label>
            <div className="relative">
              <Briefcase className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="e.g. AI Engineer..."
                value={roleInput}
                onChange={(e) => setRoleInput(e.target.value)}
                className="pl-8 h-9 text-xs"
              />
            </div>
          </div>

          {/* Location Filter */}
          <div>
            <label className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground mb-1 block">
              Location
            </label>
            <div className="relative">
              <MapPin className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="e.g. Remote, SF..."
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                className="pl-8 h-9 text-xs"
              />
            </div>
          </div>

          {/* Company Filter */}
          <div>
            <label className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground mb-1 block">
              Company
            </label>
            <div className="relative">
              <Building className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="e.g. OpenAI, Stripe..."
                value={companyInput}
                onChange={(e) => setCompanyInput(e.target.value)}
                className="pl-8 h-9 text-xs"
              />
            </div>
          </div>
        </form>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 pt-1 lg:pt-0">
          <Button
            type="button"
            size="sm"
            onClick={handleApplyTextFilters}
            className="h-9 px-3 text-xs"
          >
            <Search className="mr-1.5 h-3.5 w-3.5" />
            Apply Filters
          </Button>

          {hasActiveFilters && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="h-9 px-2.5 text-xs text-muted-foreground hover:text-foreground"
            >
              <RotateCcw className="mr-1 h-3.5 w-3.5" />
              Reset
            </Button>
          )}

          <Button
            type="button"
            variant="default"
            size="sm"
            onClick={() => runMatching({ limit: 500 })}
            disabled={runningMatch}
            className="h-9 px-3.5 text-xs bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-sm"
          >
            <Sparkles className={`mr-1.5 h-3.5 w-3.5 ${runningMatch ? 'animate-spin' : ''}`} />
            {runningMatch ? 'Scoring Jobs...' : 'Run AI Match'}
          </Button>
        </div>
      </div>
    </div>
  );
}
