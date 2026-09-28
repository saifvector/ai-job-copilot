'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sparkles, Terminal, ShieldCheck } from 'lucide-react';
import { ThemeToggle } from '@/components/common/theme-toggle';
import { Badge } from '@/components/ui/badge';
import { NAV_ITEMS } from '@/lib/constants';
import { cn } from '@/lib/utils';

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/80 bg-background/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between px-4 sm:px-8">
        {/* Logo and App Title */}
        <div className="flex items-center space-x-6">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-primary to-cyan-400 text-white shadow-md shadow-primary/20 transition-transform group-hover:scale-105">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-tight text-foreground flex items-center gap-1.5">
                AI Job Copilot
                <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4 border-primary/30 text-primary">
                  Phase 1
                </Badge>
              </span>
            </div>
          </Link>

          {/* Desktop Nav Items */}
          <nav className="hidden md:flex items-center space-x-1 pl-4">
            {NAV_ITEMS.map((item) => {
              const isActive =
                item.href === '/'
                  ? pathname === '/'
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-accent text-accent-foreground font-semibold'
                      : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Actions: API health indicator, Theme Toggle */}
        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-1.5 text-xs text-muted-foreground bg-muted/40 border border-border/60 px-2.5 py-1 rounded-full">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono">API :8000</span>
          </div>

          <ThemeToggle />

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded-md border border-border bg-card hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors"
          >
            <Terminal className="h-3.5 w-3.5" />
            Swagger Docs
          </a>
        </div>
      </div>
    </header>
  );
}
