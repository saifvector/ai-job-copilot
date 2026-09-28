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
import { SkillImpact } from '@/types';
import { Sparkles } from 'lucide-react';

interface SkillImpactChartProps {
  data: SkillImpact[];
  loading?: boolean;
}

export function SkillImpactChart({ data, loading }: SkillImpactChartProps) {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  if (loading || !isMounted) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            Skill Influence on Interview Outcomes
          </CardTitle>
          <CardDescription>Correlation between target skills and employer responses</CardDescription>
        </CardHeader>
        <CardContent className="h-[280px] flex items-center justify-center">
          <div className="h-40 w-40 rounded-full border-4 border-dashed border-muted animate-spin" />
        </CardContent>
      </Card>
    );
  }

  const topSkills = (data || []).slice(0, 8).map((s) => ({
    name: s.skillName,
    interviews: s.interviewsInfluenced,
    offers: s.offersInfluenced,
    avgScore: Number(s.averageMatchScore.toFixed(1)),
  }));

  const hasData = topSkills.length > 0;

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          Skill Influence on Interview Outcomes
        </CardTitle>
        <CardDescription>
          Count of interview and offer outcomes influenced by specific candidate competencies
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-2">
        {!hasData ? (
          <div className="h-[280px] flex flex-col items-center justify-center text-center p-6 border border-dashed rounded-lg">
            <p className="text-sm font-medium text-muted-foreground">No skill outcome correlations yet</p>
            <p className="text-xs text-muted-foreground/80 mt-1">
              Apply to jobs with extracted skills to train your skill impact matrix
            </p>
          </div>
        ) : (
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topSkills} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={90} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(23, 23, 23, 0.95)',
                    borderRadius: '8px',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Bar dataKey="interviews" name="Interviews Influenced" fill="#10b981" radius={[0, 4, 4, 0]} />
                <Bar dataKey="offers" name="Offers Influenced" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
