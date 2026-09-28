'use client';

import * as React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LocationDistributionItem } from '@/types';
import { Globe } from 'lucide-react';

interface LocationDistributionChartProps {
  data: LocationDistributionItem[];
  loading?: boolean;
}

export function LocationDistributionChart({ data, loading }: LocationDistributionChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  if (loading || !isMounted) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Globe className="h-4 w-4 text-primary" />
            Workplace Model Distribution
          </CardTitle>
          <CardDescription>Remote vs. Hybrid vs. Onsite role breakdown</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const locationColors: Record<string, string> = {
    Remote: '#10b981', // Emerald
    Hybrid: '#3b82f6', // Blue
    Onsite: '#8b5cf6', // Violet
  };

  const chartData = data.map((item) => ({
    type: item.type,
    count: item.count,
    percentage: item.percentage,
    color: locationColors[item.type] || '#6b7280',
  }));

  const total = data.reduce((acc, curr) => acc + curr.count, 0);

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Globe className="h-4 w-4 text-primary" />
            Location Distribution
          </CardTitle>
          <span className="text-xs text-muted-foreground">{total} Opportunities</span>
        </div>
        <CardDescription>Breakdown by workplace arrangement across opportunities</CardDescription>
      </CardHeader>

      <CardContent className="pt-2 flex-1">
        <div className="w-full h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border) / 0.5)" />
              <XAxis dataKey="type" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const item = payload[0].payload;
                    return (
                      <div className="rounded-lg border border-border bg-background/95 p-2.5 shadow-md backdrop-blur-sm text-xs space-y-1">
                        <p className="font-semibold text-foreground flex items-center gap-1.5">
                          <span
                            className="inline-block h-2 w-2 rounded-full"
                            style={{ backgroundColor: item.color }}
                          />
                          {item.type}
                        </p>
                        <p className="text-muted-foreground">{item.count} Jobs ({item.percentage}%)</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={40}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Proportional metric summary */}
        <div className="mt-3 grid grid-cols-3 gap-2 border-t border-border/50 pt-3 text-center">
          {chartData.map((loc) => (
            <div key={loc.type} className="p-2 rounded-lg bg-muted/30">
              <span className="text-[11px] text-muted-foreground block">{loc.type}</span>
              <span className="text-sm font-bold text-foreground">{loc.percentage}%</span>
              <span className="text-[10px] text-muted-foreground block">{loc.count} jobs</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
