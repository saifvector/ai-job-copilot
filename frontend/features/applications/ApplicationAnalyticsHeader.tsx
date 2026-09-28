'use client';

import React from 'react';
import {
  Send,
  Calendar,
  Award,
  XCircle,
  TrendingUp,
  Percent,
} from 'lucide-react';
import { ApplicationAnalytics } from '@/types';
import { Card } from '@/components/ui/card';

interface ApplicationAnalyticsHeaderProps {
  analytics: ApplicationAnalytics | null;
  loading?: boolean;
}

export function ApplicationAnalyticsHeader({
  analytics,
  loading = false,
}: ApplicationAnalyticsHeaderProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="p-4 border-border/40 bg-card/60 animate-pulse">
            <div className="h-3 w-16 bg-muted rounded mb-2" />
            <div className="h-7 w-12 bg-muted rounded" />
          </Card>
        ))}
      </div>
    );
  }

  const sent = analytics?.applicationsSent ?? 0;
  const interviews = analytics?.interviewsReceived ?? 0;
  const offers = analytics?.offersReceived ?? 0;
  const rejections = analytics?.rejections ?? 0;
  const responseRate = analytics?.responseRate ?? 0;
  const interviewRate = analytics?.interviewRate ?? 0;
  const offerRate = analytics?.offerRate ?? 0;
  const upcoming = analytics?.interviewsScheduledUpcoming ?? 0;

  const stats = [
    {
      label: 'Applications Sent',
      value: sent,
      subtitle: `${analytics?.applicationsThisMonth ?? 0} this month`,
      icon: Send,
      color: 'text-primary',
      bg: 'bg-primary/10',
    },
    {
      label: 'Interviews Reached',
      value: interviews,
      subtitle: `${upcoming} upcoming`,
      icon: Calendar,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
    },
    {
      label: 'Offers Received',
      value: offers,
      subtitle: `${offerRate}% conversion`,
      icon: Award,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
    },
    {
      label: 'Response Rate',
      value: `${responseRate}%`,
      subtitle: 'Past applied stage',
      icon: TrendingUp,
      color: 'text-amber-500',
      bg: 'bg-amber-500/10',
    },
    {
      label: 'Interview Rate',
      value: `${interviewRate}%`,
      subtitle: 'Sent to interview',
      icon: Percent,
      color: 'text-purple-500',
      bg: 'bg-purple-500/10',
    },
    {
      label: 'Rejections',
      value: rejections,
      subtitle: 'Recorded outcomes',
      icon: XCircle,
      color: 'text-rose-500',
      bg: 'bg-rose-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <Card
            key={idx}
            className="p-4 border-border/50 bg-card/70 backdrop-blur-sm hover:border-border transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-muted-foreground truncate">
                {stat.label}
              </span>
              <div className={`p-1.5 rounded-md ${stat.bg}`}>
                <Icon className={`w-3.5 h-3.5 ${stat.color}`} />
              </div>
            </div>
            <div className="text-xl font-bold tracking-tight text-foreground">
              {stat.value}
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5 truncate">
              {stat.subtitle}
            </p>
          </Card>
        );
      })}
    </div>
  );
}
