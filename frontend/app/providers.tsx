'use client';

import * as React from 'react';
import { useTheme } from '@/hooks/use-theme';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // Initialize theme side-effect listener
  useTheme();
  return <>{children}</>;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return <ThemeProvider>{children}</ThemeProvider>;
}
