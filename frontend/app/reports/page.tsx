'use client';

import React, { useEffect, useState } from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useReportStore } from '@/store';
import {
  ReportStatsHeader,
  ReportWizardModal,
  ReportHistoryTable,
  ReportPreviewModal,
} from '@/features/reports';
import {
  FileText,
  Plus,
  RefreshCw,
  AlertCircle,
  BarChart3,
  Sparkles,
  Layers,
  CheckCircle2,
  FileSpreadsheet,
  DownloadCloud,
} from 'lucide-react';
import { ExportFormat, ReportGeneratePayload, ReportType } from '@/types';

const TEMPLATES: {
  type: ReportType;
  title: string;
  description: string;
  format: ExportFormat;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}[] = [
  {
    type: 'APPLICATION_REPORT',
    title: 'Application Funnel',
    description: 'Pipeline conversion rates, status trajectory, and monthly response velocity.',
    format: 'PDF',
    icon: BarChart3,
    color: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  },
  {
    type: 'MATCH_REPORT',
    title: 'Job Match Analysis',
    description: 'Algorithmic compatibility breakdown across top opportunities.',
    format: 'PDF',
    icon: Sparkles,
    color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
  },
  {
    type: 'SKILL_REPORT',
    title: 'Skill Gap & Roadmap',
    description: 'Employer demand frequencies with prioritized P1-P3 upskilling paths.',
    format: 'XLSX',
    icon: Layers,
    color: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
  },
  {
    type: 'CAREER_REPORT',
    title: 'Career Readiness Index',
    description: 'Holistic career benchmarking, structural strength, and market alignment.',
    format: 'PDF',
    icon: CheckCircle2,
    color: 'text-indigo-500 bg-indigo-500/10 border-indigo-500/20',
  },
  {
    type: 'RESUME_REPORT',
    title: 'ATS & Resume Audit',
    description: 'ATS scores, keyword coverage density, and tailored versions history.',
    format: 'CSV',
    icon: FileText,
    color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  },
];

export default function ReportsPage() {
  const {
    reports,
    stats,
    selectedReport,
    loading,
    generating,
    downloading,
    error,
    fetchReports,
    generateReport,
    selectReportById,
    deleteReport,
    downloadReport,
    clearSelected,
    clearError,
  } = useReportStore();

  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [initialType, setInitialType] = useState<ReportType | undefined>(undefined);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleOpenWizard = (type?: ReportType) => {
    setInitialType(type);
    setIsWizardOpen(true);
  };

  const handleGenerate = async (payload: ReportGeneratePayload) => {
    const report = await generateReport(payload);
    if (report) {
      setSuccessBanner(`Successfully generated "${report.title}" in ${report.format} format.`);
      setTimeout(() => setSuccessBanner(null), 5000);
      return report;
    }
    return null;
  };

  const handleSelectReport = async (id: string) => {
    const report = await selectReportById(id);
    if (report) {
      setIsPreviewOpen(true);
    }
  };

  const handleDownload = async (id: string, fileName?: string) => {
    await downloadReport(id, fileName);
  };

  const handleDelete = async (id: string) => {
    const success = await deleteReport(id);
    if (success) {
      if (selectedReport?.id === id) {
        setIsPreviewOpen(false);
        clearSelected();
      }
    }
    return success;
  };

  const handleRefresh = () => {
    fetchReports();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Reporting & Export Center"
        description="Generate professional PDF reports, multi-sheet Excel workbooks (XLSX), CSV data feeds, and JSON archives of your career telemetry."
        badge={
          <Badge
            variant="outline"
            className="border-primary/40 bg-primary/10 text-primary font-medium"
          >
            <DownloadCloud className="w-3.5 h-3.5 mr-1 text-primary" />
            Phase 9: Export Engine
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
              className="text-xs h-8 gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
            <Button
              size="sm"
              onClick={() => handleOpenWizard()}
              className="text-xs h-8 gap-1.5 shadow-sm bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Generate Report</span>
            </Button>
          </div>
        }
      />

      {/* Success Notification */}
      {successBanner && (
        <div className="flex items-center justify-between p-3.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>{successBanner}</span>
          </div>
          <button
            onClick={() => setSuccessBanner(null)}
            className="text-xs underline hover:opacity-80"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="flex items-center justify-between p-3.5 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-400 text-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={clearError}
            className="text-xs underline hover:opacity-80"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Analytics & Stats Bar */}
      <ReportStatsHeader stats={stats} />

      {/* Quick Generation Templates Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold tracking-tight text-foreground flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>Quick Report Blueprints</span>
          </h3>
          <span className="text-xs text-muted-foreground">
            Click to launch pre-configured generator
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {TEMPLATES.map((tmpl) => {
            const Icon = tmpl.icon;
            return (
              <Card
                key={tmpl.type}
                onClick={() => handleOpenWizard(tmpl.type)}
                className="p-3.5 rounded-xl border border-border/60 hover:border-primary/50 bg-card hover:bg-muted/30 transition-all cursor-pointer group flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div
                      className={`p-2 rounded-lg border ${tmpl.color} flex items-center justify-center`}
                    >
                      <Icon className="h-4 w-4" />
                    </div>
                    <Badge variant="outline" className="text-[10px] font-mono uppercase">
                      {tmpl.format}
                    </Badge>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-foreground group-hover:text-primary transition-colors">
                      {tmpl.title}
                    </h4>
                    <p className="text-[11px] text-muted-foreground line-clamp-2 mt-0.5 leading-snug">
                      {tmpl.description}
                    </p>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-border/40 flex items-center justify-between text-[11px] text-primary font-medium opacity-80 group-hover:opacity-100">
                  <span>Generate Blueprint</span>
                  <span className="group-hover:translate-x-0.5 transition-transform">→</span>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Report History & Archive Table */}
      <ReportHistoryTable
        reports={reports}
        loading={loading}
        onPreview={(report) => {
          selectReportById(report.id);
          setIsPreviewOpen(true);
        }}
        onDownload={handleDownload}
        onDelete={handleDelete}
      />

      {/* Generation Wizard Modal */}
      <ReportWizardModal
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onGenerate={handleGenerate}
        generating={generating}
        initialType={initialType}
      />

      {/* Report Preview & Telemetry Modal */}
      <ReportPreviewModal
        report={selectedReport}
        isOpen={isPreviewOpen}
        onClose={() => {
          setIsPreviewOpen(false);
          clearSelected();
        }}
        onDownload={handleDownload}
        onDelete={handleDelete}
        isDownloading={downloading}
      />
    </div>
  );
}
