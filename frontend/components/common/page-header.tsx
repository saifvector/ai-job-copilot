import * as React from 'react';
import { cn } from '@/lib/utils';

export interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  badge?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  action,
  badge,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        'flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border/60 pb-6 mb-8',
        className
      )}
    >
      <div className="space-y-1">
        <div className="flex items-center space-x-3">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-foreground">{title}</h1>
          {badge}
        </div>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      {action && <div className="flex items-center space-x-3">{action}</div>}
    </div>
  );
}
