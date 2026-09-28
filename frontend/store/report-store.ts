import { create } from 'zustand';
import {
  ExportFormat,
  Report,
  ReportGeneratePayload,
  ReportListStats,
  ReportType,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface ReportStoreState {
  reports: Report[];
  stats: ReportListStats | null;
  selectedReport: Report | null;
  loading: boolean;
  generating: boolean;
  downloading: boolean;
  error: string | null;

  // Actions
  fetchReports: (filters?: { reportType?: string; format?: string }) => Promise<void>;
  generateReport: (payload: ReportGeneratePayload) => Promise<Report | null>;
  selectReportById: (id: string) => Promise<Report | null>;
  deleteReport: (id: string) => Promise<boolean>;
  downloadReport: (id: string, fileName?: string) => Promise<void>;
  clearSelected: () => void;
  clearError: () => void;
}

function normalizeReport(raw: any): Report {
  if (!raw) return raw;
  return {
    id: raw.id,
    userId: raw.user_id ?? raw.userId ?? '',
    reportType: (raw.report_type ?? raw.reportType ?? 'APPLICATION_REPORT') as ReportType,
    title: raw.title ?? 'Report',
    format: (raw.format ?? 'PDF') as ExportFormat,
    filePath: raw.file_path ?? raw.filePath ?? '',
    fileName: raw.file_name ?? raw.fileName ?? 'report.pdf',
    fileSize: raw.file_size ?? raw.fileSize ?? 0,
    downloadCount: raw.download_count ?? raw.downloadCount ?? 0,
    generationDurationMs: raw.generation_duration_ms ?? raw.generationDurationMs ?? 0,
    summary: raw.summary ?? null,
    generatedAt: raw.generated_at ?? raw.generatedAt ?? new Date().toISOString(),
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    downloadUrl: raw.download_url ?? raw.downloadUrl,
  };
}

function normalizeStats(raw: any): ReportListStats {
  if (!raw) {
    return {
      totalReports: 0,
      totalDownloads: 0,
      storageUsedBytes: 0,
      mostPopularType: null,
    };
  }
  return {
    totalReports: raw.total_reports ?? raw.totalReports ?? 0,
    totalDownloads: raw.total_downloads ?? raw.totalDownloads ?? 0,
    storageUsedBytes: raw.storage_used_bytes ?? raw.storageUsedBytes ?? 0,
    mostPopularType: raw.most_popular_type ?? raw.mostPopularType ?? null,
  };
}

export const useReportStore = create<ReportStoreState>((set, get) => ({
  reports: [],
  stats: null,
  selectedReport: null,
  loading: false,
  generating: false,
  downloading: false,
  error: null,

  fetchReports: async (filters) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getReports({
        report_type: filters?.reportType,
        format: filters?.format,
      });

      if (response.success && response.data) {
        const rawList = response.data.reports || [];
        const normalizedReports = rawList.map(normalizeReport);
        const normalizedStats = normalizeStats(response.data.stats);

        set({
          reports: normalizedReports,
          stats: normalizedStats,
          loading: false,
        });
      } else {
        set({ error: 'Failed to retrieve reports', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while loading reports';
      set({ error: message, loading: false });
    }
  },

  generateReport: async (payload: ReportGeneratePayload) => {
    set({ generating: true, error: null });
    try {
      const response = await apiClient.generateReport(payload);
      if (response.success && response.data) {
        const newReport = normalizeReport(response.data);
        // Prepend new report and refresh list in background
        set((state) => ({
          reports: [newReport, ...state.reports],
          generating: false,
        }));
        get().fetchReports();
        return newReport;
      } else {
        set({ error: 'Failed to generate report', generating: false });
        return null;
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Report generation encountered an error';
      set({ error: message, generating: false });
      return null;
    }
  },

  selectReportById: async (id: string) => {
    // Check locally first
    const local = get().reports.find((r) => r.id === id);
    if (local) {
      set({ selectedReport: local });
      return local;
    }

    set({ loading: true, error: null });
    try {
      const response = await apiClient.getReportById(id);
      if (response.success && response.data) {
        const report = normalizeReport(response.data);
        set({ selectedReport: report, loading: false });
        return report;
      } else {
        set({ error: 'Report not found', loading: false });
        return null;
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Failed to retrieve report details';
      set({ error: message, loading: false });
      return null;
    }
  },

  deleteReport: async (id: string) => {
    try {
      const response = await apiClient.deleteReport(id);
      if (response.success && response.data) {
        set((state) => ({
          reports: state.reports.filter((r) => r.id !== id),
          selectedReport: state.selectedReport?.id === id ? null : state.selectedReport,
        }));
        get().fetchReports();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  downloadReport: async (id: string, fileName?: string) => {
    set({ downloading: true });
    try {
      const downloadUrl = apiClient.getReportDownloadUrl(id);
      // Trigger browser download via anchor element
      const link = document.createElement('a');
      link.href = downloadUrl;
      if (fileName) {
        link.download = fileName;
      }
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Optimistically increment download count locally
      set((state) => ({
        reports: state.reports.map((r) =>
          r.id === id ? { ...r, downloadCount: r.downloadCount + 1 } : r
        ),
        stats: state.stats
          ? { ...state.stats, totalDownloads: state.stats.totalDownloads + 1 }
          : state.stats,
        downloading: false,
      }));
    } catch {
      set({ downloading: false });
    }
  },

  clearSelected: () => set({ selectedReport: null }),
  clearError: () => set({ error: null }),
}));
