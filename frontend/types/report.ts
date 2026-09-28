export type ReportType =
  | 'APPLICATION_REPORT'
  | 'MATCH_REPORT'
  | 'SKILL_REPORT'
  | 'CAREER_REPORT'
  | 'RESUME_REPORT';

export type ExportFormat = 'PDF' | 'CSV' | 'XLSX' | 'JSON';

export interface ReportGeneratePayload {
  reportType: ReportType;
  format: ExportFormat;
  title?: string;
  dateRangeDays?: number;
  includeDetails?: boolean;
}

export interface Report {
  id: string;
  userId: string;
  reportType: ReportType;
  title: string;
  format: ExportFormat;
  filePath: string;
  fileName: string;
  fileSize: number;
  downloadCount: number;
  generationDurationMs: number;
  summary?: string | null;
  generatedAt: string;
  createdAt: string;
  downloadUrl?: string;
}

export interface ReportListStats {
  totalReports: number;
  totalDownloads: number;
  storageUsedBytes: number;
  mostPopularType?: string | null;
}

export interface ReportListData {
  reports: Report[];
  stats: ReportListStats;
}
