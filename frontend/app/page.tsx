'use client';

import * as React from 'react';
import { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  ArrowRight,
  Database,
  Cpu,
  Boxes,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  Layers,
  Activity,
  Terminal,
} from 'lucide-react';
import { Navbar } from '@/components/layout/navbar';
import { Footer } from '@/components/layout/footer';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Badge,
  Input,
  Select,
  Modal,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  Spinner,
  Skeleton,
  EmptyState,
} from '@/components/ui';
import { apiClient } from '@/services/api-client';

export default function HomePage() {
  const [healthStatus, setHealthStatus] = useState<string | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  const checkHealth = async () => {
    setIsCheckingHealth(true);
    try {
      const res = await apiClient.checkRootHealth();
      setHealthStatus(res.status);
    } catch {
      setHealthStatus('unreachable (backend offline or loading)');
    } finally {
      setIsCheckingHealth(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden pt-20 pb-24 md:pt-32 md:pb-36 border-b border-border/60">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(14,165,233,0.15),rgba(255,255,255,0))]" />
          
          <div className="container relative px-4 sm:px-8 text-center max-w-4xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1 text-xs font-medium text-primary">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Phase 1 Core Architecture Ready</span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-foreground">
              Intelligent Career Copilot{' '}
              <span className="bg-gradient-to-r from-primary via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                Engineered for Scale
              </span>
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Production-ready monorepo foundation powered by Next.js 15, FastAPI Python 3.12, 
              PostgreSQL with Prisma ORM, and comprehensive DevOps orchestration.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link href="/dashboard">
                <Button size="lg" rightIcon={<ArrowRight className="h-4 w-4" />}>
                  Explore Dashboard
                </Button>
              </Link>
              <Button
                variant="outline"
                size="lg"
                onClick={checkHealth}
                isLoading={isCheckingHealth}
                leftIcon={<Activity className="h-4 w-4 text-emerald-500" />}
              >
                Probe Backend Health
              </Button>
            </div>

            {/* Health status banner */}
            {healthStatus && (
              <div className="pt-2 animate-fade-in">
                <Badge
                  variant={healthStatus === 'healthy' ? 'success' : 'destructive'}
                  className="px-3 py-1 text-xs"
                >
                  GET /health Status: {healthStatus}
                </Badge>
              </div>
            )}
          </div>
        </section>

        {/* Architectural Pillars */}
        <section className="py-20 container px-4 sm:px-8 max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-2">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-foreground">
              Architecture Overview
            </h2>
            <p className="text-muted-foreground text-sm">
              Strict isolation, type safety, and clean separation between presentation, domain, and data layers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-3">
                  <Boxes className="h-5 w-5" />
                </div>
                <CardTitle>Next.js 15 App Router</CardTitle>
                <CardDescription>
                  React 19, TypeScript strict mode, Zustand state store, and Tailwind CSS design system.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Tailwind & shadcn/ui tokens</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Zustand global stores</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Typed API client with error handling</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-3">
                  <Cpu className="h-5 w-5" />
                </div>
                <CardTitle>FastAPI Backend</CardTitle>
                <CardDescription>
                  Python 3.12 async engine, repository pattern, service layer, and correlation ID tracing.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>BaseRepository & BaseService pattern</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Pydantic v2 schemas and validation</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>GET /health & OpenAPI 3.1 Swagger</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3">
                  <Database className="h-5 w-5" />
                </div>
                <CardTitle>PostgreSQL & Prisma</CardTitle>
                <CardDescription>
                  UUID primary keys, 1-to-1 User/Profile relation, cascade deletes, and migrations.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Prisma schema & SQL migrations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Idempotent TypeScript & SQL seeds</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Async SQLAlchemy models matching Prisma</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* UI System Live Showcase */}
        <section className="py-20 border-t border-border/60 bg-muted/20">
          <div className="container px-4 sm:px-8 max-w-6xl mx-auto space-y-12">
            <div className="space-y-2">
              <Badge variant="outline">Design System</Badge>
              <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-foreground">
                Foundation Component Gallery
              </h2>
              <p className="text-sm text-muted-foreground">
                All 9 requested UI components built with Tailwind CSS, accessible states, and sleek dark mode.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Buttons & Badges */}
              <Card>
                <CardHeader>
                  <CardTitle>1. Buttons & 7. Badges</CardTitle>
                  <CardDescription>Multi-variant interactive controls</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <Button variant="default">Primary</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="outline">Outline</Button>
                    <Button variant="destructive">Destructive</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button isLoading>Loading</Button>
                  </div>
                  <div className="flex flex-wrap gap-2 pt-2">
                    <Badge variant="default">Default</Badge>
                    <Badge variant="secondary">Secondary</Badge>
                    <Badge variant="outline">Outline</Badge>
                    <Badge variant="success">Success</Badge>
                    <Badge variant="warning">Warning</Badge>
                    <Badge variant="destructive">Destructive</Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Form Controls */}
              <Card>
                <CardHeader>
                  <CardTitle>2. Input & 3. Select</CardTitle>
                  <CardDescription>Form controls with labels and helper text</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Input
                    label="Sample Input"
                    placeholder="Enter candidate email..."
                    helperText="Valid email format required"
                  />
                  <Select
                    label="Sample Select"
                    options={[
                      { label: 'Engineering (Software, AI, Cloud)', value: 'eng' },
                      { label: 'Product Management', value: 'pm' },
                      { label: 'Design & UX', value: 'design' },
                    ]}
                  />
                </CardContent>
              </Card>

              {/* Modal trigger & Loaders */}
              <Card>
                <CardHeader>
                  <CardTitle>5. Modal & 8. Loaders</CardTitle>
                  <CardDescription>Accessible Dialog and animated spinners/skeletons</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button variant="outline" onClick={() => setIsDemoModalOpen(true)}>
                    Trigger Demo Modal
                  </Button>
                  <div className="flex items-center gap-4 pt-2">
                    <Spinner size="sm" />
                    <Spinner size="md" />
                    <Spinner size="lg" />
                    <div className="w-full space-y-2">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-4 w-1/2" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Empty State */}
              <Card>
                <CardHeader>
                  <CardTitle>9. Empty State</CardTitle>
                  <CardDescription>Structured placeholder view</CardDescription>
                </CardHeader>
                <CardContent>
                  <EmptyState
                    title="No business features active"
                    description="Foundation Phase 1 established. Ready for Phase 2 pipeline integrations."
                    action={
                      <Link href="/dashboard">
                        <Button size="sm" variant="outline">
                          View Dashboard
                        </Button>
                      </Link>
                    }
                  />
                </CardContent>
              </Card>
            </div>

            {/* Table component demonstration */}
            <Card>
              <CardHeader>
                <CardTitle>6. Table Component</CardTitle>
                <CardDescription>Responsive data layout</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Service</TableHead>
                      <TableHead>Environment</TableHead>
                      <TableHead>Port</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-medium">Next.js Frontend</TableCell>
                      <TableCell>App Router</TableCell>
                      <TableCell className="font-mono">3000</TableCell>
                      <TableCell><Badge variant="success">Active</Badge></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">FastAPI Backend</TableCell>
                      <TableCell>Python 3.12</TableCell>
                      <TableCell className="font-mono">8000</TableCell>
                      <TableCell><Badge variant="success">Active</Badge></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">PostgreSQL Database</TableCell>
                      <TableCell>Prisma Schema</TableCell>
                      <TableCell className="font-mono">5432</TableCell>
                      <TableCell><Badge variant="success">Configured</Badge></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      {/* Demo Modal instance */}
      <Modal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
        title="Accessible Design System Modal"
        description="This modal demonstrates focus management, backdrop blur, ESC key dismiss, and responsive sizing."
        footer={
          <>
            <Button variant="ghost" onClick={() => setIsDemoModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsDemoModalOpen(false)}>Confirm</Button>
          </>
        }
      >
        <div className="py-2 text-sm text-muted-foreground space-y-2">
          <p>
            The UI system is completely isolated from business features as required by Phase 1 specifications.
          </p>
          <div className="rounded-md bg-muted/60 p-3 font-mono text-xs">
            Status: Foundation verified (Phase 1)
          </div>
        </div>
      </Modal>

      <Footer />
    </div>
  );
}
