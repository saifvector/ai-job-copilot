'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Settings, Shield, Server, Palette } from 'lucide-react';
import { useTheme } from '@/hooks/use-theme';

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  return (
    <AppShell>
      <PageHeader
        title="Settings"
        description="System environment parameters and client configuration."
        badge={<Badge variant="outline">System Config</Badge>}
      />

      <div className="max-w-4xl space-y-8">
        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Palette className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>Appearance & Theme</CardTitle>
                <CardDescription>Tailwind and shadcn/ui color theme selection</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="max-w-sm">
              <Select
                label="Theme Preference"
                value={theme}
                onChange={(e) => setTheme(e.target.value as 'dark' | 'light' | 'system')}
                options={[
                  { label: 'Dark Mode (Default)', value: 'dark' },
                  { label: 'Light Mode', value: 'light' },
                  { label: 'System Sync', value: 'system' },
                ]}
              />
            </div>
          </CardContent>
        </Card>

        {/* Backend Environment Info */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
                <Server className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>API & Environment</CardTitle>
                <CardDescription>FastAPI endpoints and connectivity configuration</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="FastAPI Target URL"
                defaultValue={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                disabled
                helperText="Configured via NEXT_PUBLIC_API_URL"
              />
              <Input
                label="Application Environment"
                defaultValue="development"
                disabled
                helperText="Configured via NEXT_PUBLIC_APP_ENV"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
