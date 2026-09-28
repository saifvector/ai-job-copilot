import * as React from 'react';
import Link from 'next/link';
import { Sparkles, Terminal } from 'lucide-react';

export function Footer() {
  return (
    <footer className="w-full border-t border-border/60 bg-background/50 py-8 text-xs text-muted-foreground">
      <div className="container px-4 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <div className="flex h-5 w-5 items-center justify-center rounded bg-primary/20 text-primary">
            <Sparkles className="h-3 w-3" />
          </div>
          <span className="font-semibold text-foreground">AI Job Copilot</span>
          <span>— Phase 1 Foundation Architecture</span>
        </div>
        <div className="flex items-center space-x-6">
          <Link href="/dashboard" className="hover:text-foreground transition-colors">
            Dashboard
          </Link>
          <Link href="/profile" className="hover:text-foreground transition-colors">
            Profile
          </Link>
          <Link href="/settings" className="hover:text-foreground transition-colors">
            Settings
          </Link>
          <a
            href="http://localhost:8000/health"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-foreground transition-colors font-mono"
          >
            Health Probe
          </a>
        </div>
      </div>
    </footer>
  );
}
