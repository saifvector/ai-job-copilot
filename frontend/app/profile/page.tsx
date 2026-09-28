'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { User, Shield, Briefcase, MapPin } from 'lucide-react';

export default function ProfilePage() {
  return (
    <AppShell>
      <PageHeader
        title="Candidate Profile"
        description="Configure target roles, locations, and experience settings."
        badge={<Badge variant="outline">Prisma Entity: Profile</Badge>}
      />

      <div className="max-w-4xl space-y-8">
        {/* User Account Info */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <User className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>Account Details</CardTitle>
                <CardDescription>Primary identity linked to Prisma User model</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                defaultValue="Alex Chen"
                placeholder="Jane Doe"
                disabled
                helperText="Read-only foundation placeholder"
              />
              <Input
                label="Email Address"
                defaultValue="alex.chen@example.com"
                placeholder="jane@example.com"
                disabled
                helperText="Prisma unique indexed field"
              />
            </div>
          </CardContent>
        </Card>

        {/* Profile Preferences */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
                <Briefcase className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>Job Search Preferences</CardTitle>
                <CardDescription>Mapped to Prisma Profile schema</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Target Roles (preferredRoles)
              </label>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Staff Software Engineer</Badge>
                <Badge variant="secondary">Full Stack Architect</Badge>
                <Badge variant="secondary">AI Solutions Engineer</Badge>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Target Locations (preferredLocations)
              </label>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">Remote</Badge>
                <Badge variant="outline">San Francisco, CA</Badge>
                <Badge variant="outline">New York, NY</Badge>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Years of Experience"
                type="number"
                defaultValue={8}
                disabled
                helperText="Numeric constraint (0-50)"
              />
              <div className="space-y-1.5">
                <Input
                  label="Active Resume"
                  defaultValue="Candidate Resume Document"
                  disabled
                  helperText="Managed via Resume & File Management"
                />
              </div>
            </div>
          </CardContent>
          <CardFooter className="border-t border-border/40 pt-4 flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-muted-foreground">
              Fields reflect <code>Profile</code> and <code>Resume</code> table schemas.
            </span>
            <div className="flex items-center space-x-2">
              <a href="/resume">
                <Button variant="default" size="sm">
                  Manage Resume & Upload
                </Button>
              </a>
            </div>
          </CardFooter>
        </Card>
      </div>
    </AppShell>
  );
}
