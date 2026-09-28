import React from 'react';
import { Award, Calendar } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Certification } from '@/types';

interface CertificationsSectionProps {
  certifications: Certification[];
}

export const CertificationsSection: React.FC<CertificationsSectionProps> = ({
  certifications,
}) => {
  return (
    <Card className="border border-border/80 bg-card/60 backdrop-blur-md shadow-sm transition-all hover:border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-500">
            <Award className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base md:text-lg font-semibold flex items-center gap-2">
              <span>Licenses & Certifications</span>
              <span className="text-xs font-normal text-muted-foreground">
                ({certifications.length})
              </span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Industry credentials, cloud certifications, and technical licenses
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {certifications.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No certifications extracted from resume.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {certifications.map((cert, idx) => (
              <div
                key={cert.id || `${cert.name}-${idx}`}
                className="flex items-start gap-3 p-3.5 rounded-xl border border-border/60 bg-muted/20 hover:border-border transition-all"
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-500/10 text-amber-500">
                  <Award className="h-4 w-4" />
                </div>
                <div className="space-y-1 overflow-hidden">
                  <h4 className="text-sm font-semibold text-foreground truncate">
                    {cert.name}
                  </h4>
                  <p className="text-xs font-medium text-primary truncate">
                    {cert.issuer}
                  </p>
                  {cert.issueDate && (
                    <div className="flex items-center gap-1 text-[11px] text-muted-foreground pt-0.5">
                      <Calendar className="h-3 w-3" />
                      <span>Issued {cert.issueDate}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
