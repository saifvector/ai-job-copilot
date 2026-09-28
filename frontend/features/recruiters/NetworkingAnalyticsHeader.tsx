'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { NetworkingAnalytics } from '@/types';
import {
  Users,
  MessageSquare,
  Award,
  Building2,
  TrendingUp,
  CheckCircle2,
  ArrowUpRight,
} from 'lucide-react';

interface NetworkingAnalyticsHeaderProps {
  analytics: NetworkingAnalytics | null;
  loading?: boolean;
}

export function NetworkingAnalyticsHeader({
  analytics,
  loading = false,
}: NetworkingAnalyticsHeaderProps) {
  const cards = [
    {
      title: 'Recruiters Contacted',
      value: loading ? '...' : analytics?.recruitersContacted ?? 0,
      subtext: `${analytics?.messagesSent ?? 0} total outreach touches`,
      icon: Users,
      color: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
      badge: 'Active Network',
    },
    {
      title: 'Response Rate',
      value: loading ? '...' : `${analytics?.responseRate ?? 0}%`,
      subtext: `${analytics?.responsesReceived ?? 0} replies & calls logged`,
      icon: MessageSquare,
      color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
      badge: (analytics?.responseRate ?? 0) >= 30 ? 'High Traction' : 'Standard',
    },
    {
      title: 'Referral Success Rate',
      value: loading ? '...' : `${analytics?.referralSuccessRate ?? 0}%`,
      subtext: `${analytics?.referralsReceived ?? 0} of ${analytics?.referralsRequested ?? 0} secured`,
      icon: Award,
      color: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
      badge: 'Endorsements',
    },
    {
      title: 'Companies Reached',
      value: loading ? '...' : analytics?.companiesReached ?? 0,
      subtext: 'Unique corporate networks',
      icon: Building2,
      color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
      badge: 'Market Footprint',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <Card
            key={idx}
            className="p-4 rounded-xl border border-border/60 bg-card hover:border-primary/40 transition-all shadow-sm flex flex-col justify-between"
          >
            <div className="flex items-start justify-between">
              <span className="text-xs font-medium text-muted-foreground">
                {card.title}
              </span>
              <div
                className={`p-2 rounded-lg border ${card.color} flex items-center justify-center`}
              >
                <Icon className="h-4 w-4" />
              </div>
            </div>

            <div className="mt-3">
              <div className="text-2xl font-bold tracking-tight text-foreground">
                {card.value}
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
                <span>{card.subtext}</span>
                <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-muted/60 text-foreground/80">
                  {card.badge}
                </span>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
