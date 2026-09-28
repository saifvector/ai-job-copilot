'use client';

import * as React from 'react';
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MatchDistributionData } from '@/types';
import { PieChartIcon } from 'lucide-react';

interface MatchDistributionChartProps {
  data: MatchDistributionData | null;
  loading?: boolean;
}

export function MatchDistributionChart({ data, loading }: MatchDistributionChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  if (loading || !isMounted || !data) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <PieChartIcon className="h-4 w-4 text-primary" />
            Match Quality Distribution
          </CardTitle>
          <CardDescription>Breakdown of opportunities by candidate fit tier</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-48 w-48 rounded-full border-4 border-dashed border-muted animate-spin" />
        </CardContent>
      </Card>
    );
  }

  const chartData = data.items.map((item) => ({
    name: item.name,
    value: item.value,
    color: item.color,
    percentage: item.percentage,
  }));

  const hasData = data.total > 0;

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <PieChartIcon className="h-4 w-4 text-primary" />
            Match Distribution
          </CardTitle>
          <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-primary/10 text-primary">
            {data.total} Total Evaluated
          </span>
        </div>
        <CardDescription>Candidate fit spread across analyzed job listings</CardDescription>
      </CardHeader>

      <CardContent className="pt-2 flex-1 flex flex-col items-center justify-center">
        {hasData ? (
          <div className="w-full h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-border bg-background/95 p-2.5 shadow-md backdrop-blur-sm text-xs space-y-1">
                          <p className="font-semibold text-foreground flex items-center gap-1.5">
                            <span
                              className="inline-block h-2.5 w-2.5 rounded-full"
                              style={{ backgroundColor: item.color }}
                            />
                            {item.name}
                          </p>
                          <p className="text-muted-foreground">
                            {item.value} Opportunities ({item.percentage}%)
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value) => (
                    <span className="text-xs text-muted-foreground font-medium">{value}</span>
                  )}
                />
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="45%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="py-12 text-center text-muted-foreground text-sm">
            No matching runs completed yet. Run AI Matching to view fit distribution.
          </div>
        )}

        {/* Breakdown pill badges */}
        <div className="w-full grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-border/50 text-center">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <span className="text-[11px] text-muted-foreground block">Excellent</span>
            <span className="text-sm font-bold text-emerald-500">{data.excellent}</span>
          </div>
          <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <span className="text-[11px] text-muted-foreground block">Strong</span>
            <span className="text-sm font-bold text-blue-500">{data.strong}</span>
          </div>
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <span className="text-[11px] text-muted-foreground block">Moderate</span>
            <span className="text-sm font-bold text-amber-500">{data.moderate}</span>
          </div>
          <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
            <span className="text-[11px] text-muted-foreground block">Weak</span>
            <span className="text-sm font-bold text-rose-500">{data.weak}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
