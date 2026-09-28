'use client';

import * as React from 'react';
import { Moon, Sun, Laptop } from 'lucide-react';
import { useTheme } from '@/hooks/use-theme';
import { useMounted } from '@/hooks/use-mounted';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const mounted = useMounted();

  if (!mounted) {
    return <div className="h-9 w-9 rounded-md border border-input bg-background/50" />;
  }

  const cycleTheme = () => {
    if (theme === 'dark') setTheme('light');
    else if (theme === 'light') setTheme('system');
    else setTheme('dark');
  };

  return (
    <button
      onClick={cycleTheme}
      className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-input bg-background/50 text-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      aria-label={`Current theme: ${theme}. Click to switch theme.`}
      title={`Theme: ${theme}`}
    >
      {theme === 'dark' && <Moon className="h-4 w-4 text-cyan-400" />}
      {theme === 'light' && <Sun className="h-4 w-4 text-amber-500" />}
      {theme === 'system' && <Laptop className="h-4 w-4 text-muted-foreground" />}
    </button>
  );
}
