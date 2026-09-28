'use client';

import * as React from 'react';
import { Navbar } from './navbar';
import { Sidebar } from './sidebar';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 md:p-10 container max-w-7xl">
          {children}
        </main>
      </div>
    </div>
  );
}
