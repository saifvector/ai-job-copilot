import React from 'react';
import { Mail, Phone, User, Cpu, Calendar, CheckCircle2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CandidateContact } from '@/types';

interface ProfileCardProps {
  contact?: CandidateContact | null;
  modelUsed?: string | null;
  parsedAt?: string | null;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({
  contact,
  modelUsed,
  parsedAt,
}) => {
  const formattedDate = parsedAt
    ? new Date(parsedAt).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

  return (
    <Card className="overflow-hidden border border-border/80 bg-gradient-to-r from-card via-card to-primary/5 shadow-md">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          {/* Candidate Avatar & Core Identity */}
          <div className="flex items-center gap-4">
            <div className="relative flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 via-primary/10 to-indigo-500/20 border border-primary/20 text-primary shadow-inner">
              <User className="h-8 w-8" />
              <div className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-white shadow">
                <CheckCircle2 className="h-3.5 w-3.5" />
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
                  {contact?.name || 'Verified Candidate'}
                </h2>
                <Badge variant="secondary" className="text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20">
                  AI Parsed
                </Badge>
              </div>

              {/* Contact Information */}
              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-muted-foreground">
                {contact?.email && (
                  <div className="flex items-center gap-1.5">
                    <Mail className="h-3.5 w-3.5 text-primary/70" />
                    <a
                      href={`mailto:${contact.email}`}
                      className="hover:text-foreground hover:underline transition-colors"
                    >
                      {contact.email}
                    </a>
                  </div>
                )}
                {contact?.phone && (
                  <div className="flex items-center gap-1.5">
                    <Phone className="h-3.5 w-3.5 text-primary/70" />
                    <span>{contact.phone}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Model & Processing Metadata */}
          <div className="flex flex-wrap md:flex-col items-start md:items-end gap-2 text-xs text-muted-foreground border-t md:border-t-0 pt-4 md:pt-0 border-border/50">
            <div className="flex items-center gap-1.5 bg-primary/5 px-2.5 py-1 rounded-full border border-primary/10">
              <Cpu className="h-3.5 w-3.5 text-primary" />
              <span className="font-medium text-foreground">
                {modelUsed ? modelUsed.toUpperCase() : 'GEMINI 2.5 PRO'}
              </span>
            </div>

            {formattedDate && (
              <div className="flex items-center gap-1 text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span>Extracted {formattedDate}</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
