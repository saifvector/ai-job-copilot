'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FileText,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
  Database,
  Layers,
  Sparkles,
  Briefcase,
  Target,
  BarChart3,
  HeartPulse,
  Compass,
  Wand2,
  FileDown,
  Users,
  Award,
  GraduationCap,
  Bot,
  Code2,
  Cpu,
  TrendingUp,
} from 'lucide-react';

import { useUIStore } from '@/store/ui-store';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Career Intelligence', href: '/intelligence', icon: TrendingUp },
    { name: 'AI Agents & Workflows', href: '/agents', icon: Cpu },
    { name: 'Application Assistant', href: '/application-assistant', icon: Bot },
    { name: 'Interview Prep', href: '/interview', icon: GraduationCap },
    { name: 'Application Tracker', href: '/applications', icon: Layers },
    { name: 'Recruiter CRM', href: '/recruiters', icon: Users },
    { name: 'Referral Tracker', href: '/referrals', icon: Award },
    { name: 'Reports & Exports', href: '/reports', icon: FileDown },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Match Insights', href: '/insights', icon: Compass },
    { name: 'Profile Health', href: '/profile-health', icon: HeartPulse },
    { name: 'Job Discovery', href: '/jobs', icon: Briefcase },
    { name: 'AI Matches', href: '/matching', icon: Target },
    { name: 'Resume Tailoring', href: '/resume/tailor', icon: Wand2 },
    { name: 'Resume & Files', href: '/resume', icon: FileText },
    { name: 'Resume Intelligence', href: '/resume/analysis', icon: Sparkles },
    { name: 'Profile & Preferences', href: '/profile', icon: User },
    { name: 'Developer Portal', href: '/developer', icon: Code2 },
    { name: 'System Settings', href: '/settings', icon: Settings },
  ];



  return (
    <aside
      className={cn(
        'relative flex flex-col border-r border-border/80 bg-card/30 backdrop-blur-md transition-all duration-300 ease-in-out',
        sidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      {/* Sidebar header toggle */}
      <div className="flex h-14 items-center justify-between px-3 border-b border-border/60">
        {sidebarOpen && (
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground px-2">
            Navigation
          </span>
        )}
        <button
          onClick={toggleSidebar}
          className="ml-auto inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </button>
      </div>

      {/* Nav items */}
      <div className="flex-1 space-y-1 p-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground',
                !sidebarOpen && 'justify-center px-2'
              )}
              title={!sidebarOpen ? item.name : undefined}
            >
              <Icon className={cn('h-4 w-4 shrink-0', isActive ? 'text-primary' : 'text-muted-foreground', sidebarOpen && 'mr-3')} />
              {sidebarOpen && <span className="truncate">{item.name}</span>}
            </Link>
          );
        })}
      </div>

      {/* System Status info at bottom of sidebar */}
      {sidebarOpen ? (
        <div className="m-3 rounded-lg border border-border/70 bg-background/50 p-3 text-xs space-y-2">
          <div className="font-semibold text-foreground flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-primary" />
            Stack Foundation
          </div>
          <div className="text-[11px] text-muted-foreground space-y-1">
            <div className="flex items-center justify-between">
              <span>Next.js 15:</span>
              <span className="font-mono text-emerald-500">v15.1</span>
            </div>
            <div className="flex items-center justify-between">
              <span>FastAPI:</span>
              <span className="font-mono text-emerald-500">v0.115</span>
            </div>
            <div className="flex items-center justify-between">
              <span>PostgreSQL:</span>
              <span className="font-mono text-emerald-500">Prisma</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-3 text-center text-muted-foreground">
          <Database className="h-4 w-4 mx-auto" />
        </div>
      )}
    </aside>
  );
}
