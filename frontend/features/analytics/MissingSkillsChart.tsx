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
import { MissingSkillItem } from '@/types';
import { AlertCircle } from 'lucide-react';

interface MissingSkillsChartProps {
  data: MissingSkillItem[];
  loading?: boolean;
}

export function MissingSkillsChart({ data, loading }: MissingSkillsChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  if (loading || !isMounted) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-500" />
            Top Missing Skills
          </CardTitle>
          <CardDescription>Most frequently missing qualifications across target jobs</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const chartData = data.slice(0, 8).map((item) => ({
    name: item.name,
    frequency: item.frequency,
    importance: item.importance,
    color:
      item.importance === 'High'
        ? '#ef4444' // Rose / Red
        : item.importance === 'Medium'
        ? '#f59e0b' // Amber
        : '#3b82f6', // Blue
  }));

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-500" />
            Skill Gap Hotspots
          </CardTitle>
          <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500">
            High Impact
          </span>
        </div>
        <CardDescription>Skills present in matched roles not yet found on your profile</CardDescription>
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
                  width={90}
                  tickLine={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-border bg-background/95 p-2.5 shadow-md backdrop-blur-sm text-xs space-y-1">
                          <p className="font-semibold text-foreground">{item.name}</p>
                          <p className="text-rose-500 font-medium">{item.frequency} Matched Roles Missing</p>
                          <p className="text-muted-foreground">Priority: {item.importance}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar
                  dataKey="frequency"
                  radius={[0, 4, 4, 0]}
                  barSize={18}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="py-12 text-center text-muted-foreground text-sm">
            No skill gaps detected. Your profile matches current market listings!
          </div>
        )}
      </CardContent>
    </Card>
  );
}
