'use client';

import * as React from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AnalyticsSnapshotItem } from '@/types';
import { Activity, Camera, Check } from 'lucide-react';

interface ProfileProgressChartProps {
  data: AnalyticsSnapshotItem[];
  loading?: boolean;
  onRecordSnapshot?: () => Promise<boolean>;
  recordingSnapshot?: boolean;
}

export function ProfileProgressChart({
  data,
  loading,
  onRecordSnapshot,
  recordingSnapshot,
}: ProfileProgressChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);
  const [savedSuccess, setSavedSuccess] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleCapture = async () => {
    if (onRecordSnapshot) {
      const ok = await onRecordSnapshot();
      if (ok) {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 2500);
      }
    }
  };

  if (loading || !isMounted) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            Profile Progress & Trend History
          </CardTitle>
          <CardDescription>Historical tracking of profile strength, readiness, and match scores</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const chartData = data.map((item, idx) => {
    const d = new Date(item.timestamp);
    const dateLabel = isNaN(d.getTime())
      ? `Pt ${idx + 1}`
      : `${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`;

    return {
      date: dateLabel,
      profileScore: item.profileScore,
      readinessScore: item.readinessScore,
      matchScore: item.averageMatchScore,
    };
  });

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              Career Readiness & Profile Velocity
            </CardTitle>
            <CardDescription>Historical progression across matching runs and profile improvements</CardDescription>
          </div>
          {onRecordSnapshot && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleCapture}
              disabled={recordingSnapshot}
              className="text-xs h-8"
            >
              {savedSuccess ? (
                <>
                  <Check className="h-3.5 w-3.5 mr-1 text-emerald-500" />
                  Snapshot Recorded
                </>
              ) : recordingSnapshot ? (
                <>
                  <div className="h-3.5 w-3.5 mr-1 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  Recording...
                </>
              ) : (
                <>
                  <Camera className="h-3.5 w-3.5 mr-1 text-primary" />
                  Capture Snapshot
                </>
              )}
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-2 flex-1">
        <div className="w-full h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="profileGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="readinessGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="matchGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border) / 0.5)" />
              <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="hsl(var(--muted-foreground))" fontSize={11} />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="rounded-lg border border-border bg-background/95 p-3 shadow-md backdrop-blur-sm text-xs space-y-1.5 min-w-[170px]">
                        <p className="font-semibold text-foreground border-b border-border pb-1">
                          Snapshot: {label}
                        </p>
                        {payload.map((entry) => (
                          <div key={entry.name} className="flex items-center justify-between gap-4">
                            <span className="flex items-center gap-1.5 text-muted-foreground">
                              <span
                                className="inline-block h-2 w-2 rounded-full"
                                style={{ backgroundColor: entry.color }}
                              />
                              {entry.name}
                            </span>
                            <span className="font-bold font-mono text-foreground">
                              {entry.value}%
                            </span>
                          </div>
                        ))}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                verticalAlign="bottom"
                height={30}
                formatter={(val) => <span className="text-xs text-muted-foreground font-medium">{val}</span>}
              />
              <Area
                type="monotone"
                name="Career Readiness"
                dataKey="readinessScore"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#readinessGrad)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                name="Profile Health"
                dataKey="profileScore"
                stroke="#8b5cf6"
                fillOpacity={1}
                fill="url(#profileGrad)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                name="Avg Match Score"
                dataKey="matchScore"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#matchGrad)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
