import React from 'react';
import { Briefcase, Calendar } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Experience } from '@/types';

interface ExperienceSectionProps {
  experience: Experience[];
}

export const ExperienceSection: React.FC<ExperienceSectionProps> = ({ experience }) => {
  return (
    <Card className="border border-border/80 bg-card/60 backdrop-blur-md shadow-sm transition-all hover:border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <Briefcase className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base md:text-lg font-semibold flex items-center gap-2">
              <span>Work Experience</span>
              <span className="text-xs font-normal text-muted-foreground">
                ({experience.length})
              </span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Professional career timeline and technical responsibilities
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {experience.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No work experience extracted from resume.
          </div>
        ) : (
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
            {experience.map((exp, idx) => (
              <div key={exp.id || `${exp.company}-${idx}`} className="relative space-y-2">
                {/* Timeline node */}
                <div className="absolute -left-[27px] top-1.5 h-3.5 w-3.5 rounded-full border-2 border-primary bg-background shadow" />

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <div>
                    <h4 className="text-base font-semibold text-foreground">
                      {exp.role}
                    </h4>
                    <span className="text-sm font-medium text-primary">
                      {exp.company}
                    </span>
                  </div>

                  {(exp.startDate || exp.endDate) && (
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/40 px-2.5 py-1 rounded-full w-fit">
                      <Calendar className="h-3 w-3" />
                      <span>
                        {exp.startDate || 'N/A'} &mdash; {exp.endDate || 'Present'}
                      </span>
                    </div>
                  )}
                </div>

                {exp.description && (
                  <p className="text-xs md:text-sm text-muted-foreground leading-relaxed whitespace-pre-line pt-1">
                    {exp.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
