import React from 'react';
import { GraduationCap, Calendar } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Education } from '@/types';

interface EducationSectionProps {
  education: Education[];
}

export const EducationSection: React.FC<EducationSectionProps> = ({ education }) => {
  return (
    <Card className="border border-border/80 bg-card/60 backdrop-blur-md shadow-sm transition-all hover:border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500/10 text-sky-500">
            <GraduationCap className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base md:text-lg font-semibold flex items-center gap-2">
              <span>Education</span>
              <span className="text-xs font-normal text-muted-foreground">
                ({education.length})
              </span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Academic credentials, degrees, and university background
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {education.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No academic background extracted from resume.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {education.map((edu, idx) => (
              <div
                key={edu.id || `${edu.institution}-${idx}`}
                className="p-4 rounded-xl border border-border/60 bg-muted/20 space-y-2 hover:border-border transition-all"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-sm md:text-base font-semibold text-foreground">
                      {edu.degree}
                    </h4>
                    <p className="text-xs md:text-sm font-medium text-primary">
                      {edu.institution}
                    </p>
                  </div>
                  {(edu.startDate || edu.endDate) && (
                    <div className="flex items-center gap-1 text-[11px] text-muted-foreground bg-muted/60 px-2 py-0.5 rounded-full shrink-0">
                      <Calendar className="h-3 w-3" />
                      <span>
                        {edu.startDate ? `${edu.startDate} - ` : ''}
                        {edu.endDate || 'Present'}
                      </span>
                    </div>
                  )}
                </div>

                {edu.fieldOfStudy && (
                  <p className="text-xs text-muted-foreground">
                    Field of Study: <span className="font-medium text-foreground">{edu.fieldOfStudy}</span>
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
