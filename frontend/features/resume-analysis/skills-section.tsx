import React, { useState, useMemo } from 'react';
import { Code2, Filter, Layers } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skill, SkillCategory } from '@/types';

interface SkillsSectionProps {
  skills: Skill[];
}

const CATEGORY_STYLES: Record<
  SkillCategory | 'Other',
  { badge: string; border: string; bg: string; text: string }
> = {
  'Programming Language': {
    badge: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
    border: 'border-blue-500/30',
    bg: 'bg-blue-500/5',
    text: 'text-blue-600 dark:text-blue-400',
  },
  Framework: {
    badge: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
    border: 'border-purple-500/30',
    bg: 'bg-purple-500/5',
    text: 'text-purple-600 dark:text-purple-400',
  },
  Database: {
    badge: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/5',
    text: 'text-emerald-600 dark:text-emerald-400',
  },
  Cloud: {
    badge: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20',
    border: 'border-sky-500/30',
    bg: 'bg-sky-500/5',
    text: 'text-sky-600 dark:text-sky-400',
  },
  'AI/ML': {
    badge: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/5',
    text: 'text-amber-600 dark:text-amber-400',
  },
  Tool: {
    badge: 'bg-teal-500/10 text-teal-600 dark:text-teal-400 border-teal-500/20',
    border: 'border-teal-500/30',
    bg: 'bg-teal-500/5',
    text: 'text-teal-600 dark:text-teal-400',
  },
  Other: {
    badge: 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border-zinc-500/20',
    border: 'border-zinc-500/30',
    bg: 'bg-zinc-500/5',
    text: 'text-zinc-600 dark:text-zinc-400',
  },
};

export const SkillsSection: React.FC<SkillsSectionProps> = ({ skills }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const categories = useMemo(() => {
    const unique = Array.from(new Set(skills.map((s) => s.category)));
    return ['All', ...unique];
  }, [skills]);

  const filteredSkills = useMemo(() => {
    if (selectedCategory === 'All') return skills;
    return skills.filter((s) => s.category === selectedCategory);
  }, [skills, selectedCategory]);

  return (
    <Card className="border border-border/80 bg-card/60 backdrop-blur-md shadow-sm transition-all hover:border-border">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Code2 className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base md:text-lg font-semibold flex items-center gap-2">
              <span>Verified Competencies</span>
              <span className="text-xs font-normal text-muted-foreground">
                ({skills.length} skills detected)
              </span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Categorized technical skills with AI-evaluated proficiency confidence
            </p>
          </div>
        </div>

        {/* Category Filter Tabs */}
        {skills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 p-1 bg-muted/40 rounded-lg border border-border/50 text-xs">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                  selectedCategory === cat
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}
      </CardHeader>

      <CardContent>
        {skills.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No technical skills identified in the uploaded document.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredSkills.map((skill) => {
              const styles =
                CATEGORY_STYLES[skill.category] || CATEGORY_STYLES.Other;
              const percent = Math.round(skill.confidenceScore * 100);

              return (
                <div
                  key={skill.id || skill.name}
                  className={`flex items-center justify-between p-3 rounded-lg border ${styles.border} ${styles.bg} transition-all hover:shadow-sm`}
                >
                  <div className="space-y-1">
                    <span className="text-sm font-semibold text-foreground">
                      {skill.name}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-[10px] font-medium ${styles.text}`}>
                        {skill.category}
                      </span>
                    </div>
                  </div>

                  {/* Confidence score pill */}
                  <div className="flex flex-col items-end gap-1">
                    <div className="flex items-center gap-1">
                      <div className="h-1.5 w-12 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full transition-all duration-500"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold tabular-nums text-muted-foreground">
                        {percent}%
                      </span>
                    </div>
                    <span className="text-[10px] text-muted-foreground">
                      confidence
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
