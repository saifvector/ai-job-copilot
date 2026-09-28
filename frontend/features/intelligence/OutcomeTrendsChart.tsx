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
import { TrendPoint } from '@/types';
import { TrendingUp } from 'lucide-react';

interface OutcomeTrendsChartProps {
  data: TrendPoint[];
  loading?: boolean;
}

export function OutcomeTrendsChart({ data, loading }: OutcomeTrendsChartProps) {
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
            Outcome Trajectory & Pipeline Velocity
          </CardTitle>
          <CardDescription>Historical application, interview, and offer rates</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-40 w-40 rounded-full border-4 border-dashed border-muted animate-spin" />
        </CardContent>
      </Card>
    );
  }

  const hasData = data && data.length > 0;

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            Outcome Trajectory & Pipeline Velocity
          </CardTitle>
        </div>
        <CardDescription>
          Tracking submissions, interviews received, and offer outcomes across historical intervals
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-2">
        {!hasData ? (
          <div className="h-[280px] flex flex-col items-center justify-center text-center p-6 border border-dashed rounded-lg">
            <p className="text-sm font-medium text-muted-foreground">No outcome telemetry recorded yet</p>
            <p className="text-xs text-muted-foreground/80 mt-1">
              Log application updates or outcomes to view velocity curves
            </p>
          </div>
        ) : (
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorApps" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorInterviews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorOffers" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(23, 23, 23, 0.95)',
                    borderRadius: '8px',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Area
                  type="monotone"
                  dataKey="applications"
                  name="Applications Sent"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorApps)"
                />
                <Area
                  type="monotone"
                  dataKey="interviews"
                  name="Interviews Received"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorInterviews)"
                />
                <Area
                  type="monotone"
                  dataKey="offers"
                  name="Offers Received"
                  stroke="#8b5cf6"
                  fillOpacity={1}
                  fill="url(#colorOffers)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
