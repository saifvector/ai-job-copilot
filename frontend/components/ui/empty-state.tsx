import * as React from 'react';
import { cn } from '@/lib/utils';
import { Inbox } from 'lucide-react';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
  secondaryAction?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex min-h-[300px] flex-col items-center justify-center rounded-xl border border-dashed border-border/80 p-8 text-center animate-fade-in',
        className
      )}
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted/50 border border-border text-muted-foreground shadow-inner mb-4">
        {icon || <Inbox className="h-8 w-8 stroke-[1.5]" />}
      </div>
      <h3 className="text-base font-semibold tracking-tight text-foreground">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-muted-foreground">{description}</p>
      {(action || secondaryAction) && (
        <div className="mt-6 flex items-center space-x-3">
          {action}
          {secondaryAction}
        </div>
      )}
    </div>
  );
}
