'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { MatchScoreCategory } from '@/types';

export function getScoreCategory(score: number): {
  category: MatchScoreCategory;
  label: string;
  badgeClass: string;
  colorHex: string;
  textClass: string;
  bgClass: string;
} {
  if (score >= 90) {
    return {
      category: 'excellent',
      label: 'Excellent Fit',
      badgeClass: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
      colorHex: '#10b981',
      textClass: 'text-emerald-400',
      bgClass: 'bg-emerald-500',
    };
  }
  if (score >= 75) {
    return {
      category: 'strong',
      label: 'Strong Fit',
      badgeClass: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
      colorHex: '#3b82f6',
      textClass: 'text-blue-400',
      bgClass: 'bg-blue-500',
    };
  }
  if (score >= 60) {
    return {
      category: 'moderate',
      label: 'Moderate Fit',
      badgeClass: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      colorHex: '#f59e0b',
      textClass: 'text-amber-400',
      bgClass: 'bg-amber-500',
    };
  }
  return {
    category: 'weak',
    label: 'Weak Fit',
    badgeClass: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    colorHex: '#f43f5e',
    textClass: 'text-rose-400',
    bgClass: 'bg-rose-500',
  };
}

interface CircularScoreProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  className?: string;
}

export function CircularScoreIndicator({
  score,
  size = 54,
  strokeWidth = 4.5,
  showLabel = false,
  className,
}: CircularScoreProps) {
  const rounded = Math.round(score);
  const { label, colorHex, textClass, badgeClass } = getScoreCategory(rounded);

  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (circumference * Math.min(100, Math.max(0, rounded))) / 100;

  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="rotate-[-90deg]">
          {/* Background circle track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-border/40"
          />
          {/* Animated score circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke={colorHex}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <span className={cn('absolute text-xs font-bold tracking-tight', textClass)}>
          {rounded}%
        </span>
      </div>

      {showLabel && (
        <span className={cn('text-xs px-2 py-0.5 rounded-full border font-medium', badgeClass)}>
          {label}
        </span>
      )}
    </div>
  );
}

interface ScoreProgressBarProps {
  label: string;
  weightLabel: string;
  score: number;
  className?: string;
}

export function ScoreProgressBar({
  label,
  weightLabel,
  score,
  className,
}: ScoreProgressBarProps) {
  const rounded = Math.round(score);
  const { bgClass, textClass } = getScoreCategory(rounded);

  return (
    <div className={cn('space-y-1.5', className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-foreground flex items-center gap-1.5">
          {label}
          <span className="text-[10px] text-muted-foreground font-mono">({weightLabel})</span>
        </span>
        <span className={cn('font-semibold font-mono', textClass)}>{rounded}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-border/40 overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500 ease-out', bgClass)}
          style={{ width: `${Math.min(100, Math.max(0, rounded))}%` }}
        />
      </div>
    </div>
  );
}
