import React, { useState } from 'react';
import { Sparkles, Copy, Check } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface SummarySectionProps {
  summary?: string | null;
}

export const SummarySection: React.FC<SummarySectionProps> = ({ summary }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!summary) return;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="border border-border/80 bg-card/60 backdrop-blur-md shadow-sm transition-all hover:border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base md:text-lg font-semibold">
              Executive AI Summary
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Gemini-generated synthesis of your background and domain expertise
            </p>
          </div>
        </div>

        {summary && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-foreground"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-500" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </Button>
        )}
      </CardHeader>

      <CardContent>
        {summary ? (
          <blockquote className="rounded-lg border-l-4 border-primary/50 bg-primary/5 p-4 text-sm md:text-base leading-relaxed text-foreground italic">
            &ldquo;{summary}&rdquo;
          </blockquote>
        ) : (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No professional summary generated yet. Upload and parse a resume to synthesize your summary.
          </div>
        )}
      </CardContent>
    </Card>
  );
};
