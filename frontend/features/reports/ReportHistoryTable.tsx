'use client';

import React, { useState } from 'react';
import {
  Download,
  Eye,
  Trash2,
  FileText,
  FileSpreadsheet,
  FileCode,
  Search,
  Clock,
  HardDrive,
  Filter,
} from 'lucide-react';
import { ExportFormat, Report, ReportType } from '@/types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ReportHistoryTableProps {
  reports: Report[];
  loading: boolean;
  onPreview: (report: Report) => void;
  onDownload: (id: string, fileName?: string) => void;
  onDelete: (id: string) => void;
}

export function ReportHistoryTable({
  reports,
  loading,
  onPreview,
  onDownload,
  onDelete,
}: ReportHistoryTableProps) {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [formatFilter, setFormatFilter] = useState<string>('ALL');

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const getFormatBadge = (fmt: ExportFormat) => {
    switch (fmt) {
      case 'PDF':
        return (
          <Badge variant="outline" className="text-[10px] bg-rose-500/10 text-rose-500 border-rose-500/30 gap-1">
            <FileText className="w-3 h-3" />
            <span>PDF</span>
          </Badge>
        );
      case 'XLSX':
        return (
          <Badge variant="outline" className="text-[10px] bg-emerald-500/10 text-emerald-500 border-emerald-500/30 gap-1">
            <FileSpreadsheet className="w-3 h-3" />
            <span>XLSX</span>
          </Badge>
        );
      case 'CSV':
        return (
          <Badge variant="outline" className="text-[10px] bg-blue-500/10 text-blue-500 border-blue-500/30 gap-1">
            <FileSpreadsheet className="w-3 h-3" />
            <span>CSV</span>
          </Badge>
        );
      case 'JSON':
        return (
          <Badge variant="outline" className="text-[10px] bg-amber-500/10 text-amber-500 border-amber-500/30 gap-1">
            <FileCode className="w-3 h-3" />
            <span>JSON</span>
          </Badge>
        );
      default:
        return <Badge variant="outline">{fmt}</Badge>;
    }
  };

  const getTypeBadge = (type: ReportType) => {
    const label = type.replace('_REPORT', '').replace('_', ' ');
    return (
      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground px-2 py-0.5 rounded bg-muted/60 border border-border/40">
        {label}
      </span>
    );
  };

  const filteredReports = reports.filter((r) => {
    const matchesSearch =
      r.title.toLowerCase().includes(search.toLowerCase()) ||
      r.fileName.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'ALL' || r.reportType === typeFilter;
    const matchesFormat = formatFilter === 'ALL' || r.format === formatFilter;
    return matchesSearch && matchesType && matchesFormat;
  });

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search generated reports..."
            className="pl-9 text-xs h-9"
          />
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter:</span>
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="text-xs bg-background border border-border/60 rounded-lg px-2.5 py-1.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="ALL">All Categories</option>
            <option value="APPLICATION_REPORT">Applications</option>
            <option value="MATCH_REPORT">Job Matches</option>
            <option value="SKILL_REPORT">Skill Gaps</option>
            <option value="CAREER_REPORT">Career Readiness</option>
            <option value="RESUME_REPORT">Resume ATS</option>
          </select>

          <select
            value={formatFilter}
            onChange={(e) => setFormatFilter(e.target.value)}
            className="text-xs bg-background border border-border/60 rounded-lg px-2.5 py-1.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="ALL">All Formats</option>
            <option value="PDF">PDF</option>
            <option value="XLSX">Excel (XLSX)</option>
            <option value="CSV">CSV</option>
            <option value="JSON">JSON</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="rounded-xl border border-border/60 bg-card overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted/40 border-b border-border/60 text-muted-foreground font-semibold">
              <tr>
                <th className="py-3 px-4">Report Title & Type</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Date Generated</th>
                <th className="py-3 px-4">Size</th>
                <th className="py-3 px-4">Downloads</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {loading && filteredReports.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-muted-foreground text-xs">
                    Loading reports...
                  </td>
                </tr>
              ) : filteredReports.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-muted-foreground space-y-2">
                    <FileText className="w-8 h-8 text-muted-foreground/30 mx-auto" />
                    <p className="font-medium text-foreground text-xs">No reports generated yet</p>
                    <p className="text-[11px] text-muted-foreground">
                      Use the "Generate Report" wizard above to create PDF, Excel, or CSV exports.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredReports.map((report) => {
                  const date = new Date(report.generatedAt);
                  const dateFormatted = !isNaN(date.getTime())
                    ? date.toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })
                    : 'Recent';
                  const timeFormatted = !isNaN(date.getTime())
                    ? date.toLocaleTimeString(undefined, {
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                    : '';

                  return (
                    <tr
                      key={report.id}
                      className="hover:bg-muted/20 transition-colors group"
                    >
                      {/* Title & Type */}
                      <td className="py-3 px-4 max-w-sm">
                        <div className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                          {report.title}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          {getTypeBadge(report.reportType)}
                          <span className="text-[10px] text-muted-foreground truncate max-w-[200px]">
                            {report.fileName}
                          </span>
                        </div>
                      </td>

                      {/* Format Badge */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        {getFormatBadge(report.format)}
                      </td>

                      {/* Generated Date */}
                      <td className="py-3 px-4 whitespace-nowrap text-muted-foreground">
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3 h-3 text-muted-foreground/70" />
                          <span>{dateFormatted}</span>
                          <span className="text-[10px] text-muted-foreground/70">
                            {timeFormatted}
                          </span>
                        </div>
                      </td>

                      {/* File Size */}
                      <td className="py-3 px-4 whitespace-nowrap text-muted-foreground font-mono text-[11px]">
                        {formatBytes(report.fileSize)}
                      </td>

                      {/* Download Count */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Download className="w-3 h-3 text-muted-foreground/70" />
                          <span className="font-medium text-foreground">{report.downloadCount}</span>
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 whitespace-nowrap text-right space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onPreview(report)}
                          className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground hover:bg-muted"
                          title="Preview Report Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </Button>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDownload(report.id, report.fileName)}
                          className="h-7 w-7 p-0 text-primary hover:text-primary hover:bg-primary/10"
                          title="Download File"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </Button>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDelete(report.id)}
                          className="h-7 w-7 p-0 text-rose-500 hover:text-rose-600 hover:bg-rose-500/10"
                          title="Delete Report"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
