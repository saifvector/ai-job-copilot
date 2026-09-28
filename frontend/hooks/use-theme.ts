'use client';

import { useEffect } from 'react';
import { useUIStore } from '@/store/ui-store';

/**
 * Hook to manage HTML class dark/light mode toggle.
 */
export function useTheme() {
  const { theme, setTheme } = useUIStore();

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.add(systemDark ? 'dark' : 'light');
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  return { theme, setTheme };
}
