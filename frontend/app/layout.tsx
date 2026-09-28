import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'AI Job Copilot - Intelligent Career Automation Foundation',
  description:
    'Production-grade foundation for AI Job Copilot. Automated job matching, resume intelligence, and career co-pilot.',
  keywords: ['AI Job Copilot', 'Job Search', 'Career Agent', 'FastAPI', 'Next.js 15'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
