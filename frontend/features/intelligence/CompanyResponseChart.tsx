'use client';

import * as React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CompanyResponseMetric } from '@/types';
import { Building2 } from 'lucide-react';

interface CompanyResponseChartProps {
  data: CompanyResponseMetric[];
  loading?: boolean;
}

export function CompanyResponseChart({ data, loading }: CompanyResponseChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  if (loading || !isMounted) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Building2 className="h-4 w-4 text-primary" />
            Company Responsiveness
          </CardTitle>
          <CardDescription>Response rates across hiring organizations</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-40 w-40 rounded-full border-4 border-dashed border-muted animate-spin" />
        </CardContent>
      </Card>
    );
  }

  const chartData = (data || []).slice(0, 6).map((c) => ({
    name: c.company.slice(0, 15),
    sent: c.applicationsSent,
    responses: c.responsesReceived,
    interviews: c.interviewsCount,
  }));

  const hasData = chartData.length > 0;

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Building2 className="h-4 w-4 text-primary" />
          Company Responsiveness
        </CardTitle>
        <CardDescription>
          Submissions vs responses and interview conversion by employer
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-2">
        {!hasData ? (
          <div className="h-[280px] flex flex-col items-center justify-center text-center p-6 border border-dashed rounded-lg">
            <p className="text-sm font-medium text-muted-foreground">No employer response data yet</p>
            <p className="text-xs text-muted-foreground/80 mt-1">
              Responses and outcomes will populate as employers interact with submissions
            </p>
          </div>
        ) : (
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(23, 23, 23, 0.95)',
                    borderRadius: '8px',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar dataKey="sent" name="Submissions" fill="#64748b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="responses" name="Responses" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="interviews" name="Interviews" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
