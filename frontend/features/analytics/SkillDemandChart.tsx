'use client';

import * as React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TopSkillDemandItem } from '@/types';
import { TrendingUp } from 'lucide-react';

interface SkillDemandChartProps {
  data: TopSkillDemandItem[];
  loading?: boolean;
}

export function SkillDemandChart({ data, loading }: SkillDemandChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  if (loading || !isMounted) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            Most Demanded Skills
          </CardTitle>
          <CardDescription>Frequency of technical competencies across matched openings</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const chartData = data.slice(0, 8).map((item) => ({
    name: item.name,
    demand: item.demand,
    valueScore: item.valueScore,
  }));

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            Top In-Demand Skills
          </CardTitle>
          <span className="text-xs text-muted-foreground">Market Frequency</span>
        </div>
        <CardDescription>Most sought-after technologies identified in matched roles</CardDescription>
      </CardHeader>

      <CardContent className="pt-2 flex-1">
        {chartData.length > 0 ? (
          <div className="w-full h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border) / 0.5)" />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  width={80}
                  tickLine={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-border bg-background/95 p-2.5 shadow-md backdrop-blur-sm text-xs space-y-1">
                          <p className="font-semibold text-foreground">{item.name}</p>
                          <p className="text-primary font-medium">{item.demand} Open Opportunities</p>
                          <p className="text-muted-foreground">{item.valueScore}% of matched roles</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar
                  dataKey="demand"
                  fill="hsl(var(--primary))"
                  radius={[0, 4, 4, 0]}
                  barSize={18}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="py-12 text-center text-muted-foreground text-sm">
            No skill demand data available yet.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
