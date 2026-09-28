'use client';

import React from 'react';
import {
  FileText,
  Download,
  HardDrive,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import { ReportListStats } from '@/types';

interface ReportStatsHeaderProps {
  stats: ReportListStats | null;
  loading?: boolean;
}

export function ReportStatsHeader({ stats, loading = false }: ReportStatsHeaderProps) {
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const cards = [
    {
      title: 'Total Reports',
      value: stats ? stats.totalReports.toString() : '0',
      subtitle: 'Active generated exports',
      icon: FileText,
      color: 'text-indigo-500',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/20',
    },
    {
      title: 'Total Downloads',
      value: stats ? stats.totalDownloads.toString() : '0',
      subtitle: 'Files exported & saved',
      icon: Download,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    },
    {
      title: 'Storage Used',
      value: stats ? formatBytes(stats.storageUsedBytes) : '0 B',
      subtitle: 'Disk footprint on server',
      icon: HardDrive,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    },
    {
      title: 'Top Report Category',
      value: stats?.mostPopularType
        ? stats.mostPopularType.replace('_REPORT', '').replace('_', ' ')
        : 'Performance',
      subtitle: 'Most frequent export type',
      icon: Sparkles,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl border ${card.borderColor} bg-card/60 backdrop-blur-xs shadow-xs space-y-2`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">{card.title}</span>
              <div className={`p-1.5 rounded-lg ${card.bgColor}`}>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
            </div>
            <div>
              <div className="text-xl font-bold text-foreground">
                {loading ? '...' : card.value}
              </div>
              <p className="text-[11px] text-muted-foreground mt-0.5">{card.subtitle}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
