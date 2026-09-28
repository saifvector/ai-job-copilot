import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useReportStore } from '../store/report-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { Report, ReportListStats } from '../types/report';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getReports: vi.fn(),
      getReportById: vi.fn(),
      generateReport: vi.fn(),
      deleteReport: vi.fn(),
      getReportDownloadUrl: vi.fn(),
    },
  };
});

const mockReport: Report = {
  id: 'rep-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  reportType: 'APPLICATION_REPORT',
  title: 'Quarterly Application Funnel Report',
  format: 'PDF',
  filePath: 'reports/u-1/rep-1.pdf',
  fileName: 'Application_Performance_Report_20260927.pdf',
  fileSize: 45000,
  downloadCount: 2,
  generationDurationMs: 145,
  summary: 'Strong conversion performance with 28% interview conversion.',
  generatedAt: '2026-09-27T12:00:00Z',
  createdAt: '2026-09-27T12:00:00Z',
};

const mockStats: ReportListStats = {
  totalReports: 1,
  totalDownloads: 2,
  storageUsedBytes: 45000,
  mostPopularType: 'APPLICATION_REPORT',
};

describe('useReportStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useReportStore.setState({
      reports: [],
      stats: null,
      selectedReport: null,
      loading: false,
      generating: false,
      downloading: false,
      error: null,
    });
  });

  describe('fetchReports', () => {
    it('successfully fetches and stores reports with stats', async () => {
      vi.mocked(apiClient.getReports).mockResolvedValueOnce({
        success: true,
        data: {
          reports: [mockReport as any],
          stats: mockStats as any,
        },
        timestamp: '2026-09-27T12:00:00Z',
      });

      await useReportStore.getState().fetchReports();

      const state = useReportStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.reports).toHaveLength(1);
      expect(state.reports[0].id).toBe(mockReport.id);
      expect(state.reports[0].title).toBe(mockReport.title);
      expect(state.stats?.totalReports).toBe(1);
      expect(state.stats?.totalDownloads).toBe(2);
    });

    it('handles api failure when fetching reports', async () => {
      vi.mocked(apiClient.getReports).mockRejectedValueOnce(
        new ApiClientError('Network disconnected', 503)
      );

      await useReportStore.getState().fetchReports();

      const state = useReportStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Network disconnected');
      expect(state.reports).toHaveLength(0);
    });
  });

  describe('generateReport', () => {
    it('successfully triggers report generation and prepends report', async () => {
      const newReport: Report = {
        ...mockReport,
        id: 'rep-00000000-0000-0000-0000-000000000002',
        title: 'Skill Gap Breakdown',
        reportType: 'SKILL_REPORT',
      };

      vi.mocked(apiClient.generateReport).mockResolvedValueOnce({
        success: true,
        data: newReport as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      vi.mocked(apiClient.getReports).mockResolvedValueOnce({
        success: true,
        data: {
          reports: [newReport as any, mockReport as any],
          stats: { ...mockStats, totalReports: 2 },
        },
        timestamp: '2026-09-27T12:00:00Z',
      });

      const result = await useReportStore.getState().generateReport({
        reportType: 'SKILL_REPORT',
        format: 'PDF',
        title: 'Skill Gap Breakdown',
      });

      expect(result).not.toBeNull();
      expect(result?.id).toBe(newReport.id);

      const state = useReportStore.getState();
      expect(state.generating).toBe(false);
      expect(state.error).toBeNull();
      expect(state.reports[0].title).toBe('Skill Gap Breakdown');
    });

    it('handles report generation failure', async () => {
      vi.mocked(apiClient.generateReport).mockRejectedValueOnce(
        new ApiClientError('LLM synthesis failed', 500)
      );

      const result = await useReportStore.getState().generateReport({
        reportType: 'MATCH_REPORT',
        format: 'XLSX',
      });

      expect(result).toBeNull();
      const state = useReportStore.getState();
      expect(state.generating).toBe(false);
      expect(state.error).toBe('LLM synthesis failed');
    });
  });

  describe('selectReportById', () => {
    it('selects report from local store if present', async () => {
      useReportStore.setState({ reports: [mockReport] });

      const result = await useReportStore.getState().selectReportById(mockReport.id);

      expect(result).toEqual(mockReport);
      expect(useReportStore.getState().selectedReport).toEqual(mockReport);
      expect(apiClient.getReportById).not.toHaveBeenCalled();
    });

    it('fetches report from server if not found in local store', async () => {
      vi.mocked(apiClient.getReportById).mockResolvedValueOnce({
        success: true,
        data: mockReport as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const result = await useReportStore.getState().selectReportById('non-local-id');

      expect(result).not.toBeNull();
      expect(result?.id).toBe(mockReport.id);
      expect(useReportStore.getState().selectedReport?.id).toBe(mockReport.id);
    });
  });

  describe('deleteReport', () => {
    it('removes report from store and clears selected report if matched', async () => {
      useReportStore.setState({
        reports: [mockReport],
        selectedReport: mockReport,
      });

      vi.mocked(apiClient.deleteReport).mockResolvedValueOnce({
        success: true,
        data: true,
        timestamp: '2026-09-27T12:00:00Z',
      });

      vi.mocked(apiClient.getReports).mockResolvedValueOnce({
        success: true,
        data: { reports: [], stats: { ...mockStats, totalReports: 0 } },
        timestamp: '2026-09-27T12:00:00Z',
      });

      const success = await useReportStore.getState().deleteReport(mockReport.id);

      expect(success).toBe(true);
      const state = useReportStore.getState();
      expect(state.reports).toHaveLength(0);
      expect(state.selectedReport).toBeNull();
    });
  });

  describe('downloadReport', () => {
    it('triggers download and increments download count locally', async () => {
      useReportStore.setState({
        reports: [mockReport],
        stats: mockStats,
      });

      vi.mocked(apiClient.getReportDownloadUrl).mockReturnValueOnce(
        'http://localhost:8000/api/v1/reports/rep-1/download'
      );

      // Mock DOM element creation and click
      const mockClick = vi.fn();
      const originalCreateElement = document.createElement.bind(document);
      vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
        if (tagName === 'a') {
          return {
            href: '',
            download: '',
            target: '',
            click: mockClick,
          } as any;
        }
        return originalCreateElement(tagName);
      });
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => null as any);
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => null as any);

      await useReportStore.getState().downloadReport(mockReport.id, 'custom_report.pdf');

      expect(mockClick).toHaveBeenCalled();
      const state = useReportStore.getState();
      expect(state.reports[0].downloadCount).toBe(3);
      expect(state.stats?.totalDownloads).toBe(3);
    });
  });

  describe('utility actions', () => {
    it('clears selected report and error correctly', () => {
      useReportStore.setState({
        selectedReport: mockReport,
        error: 'Sample error message',
      });

      useReportStore.getState().clearSelected();
      expect(useReportStore.getState().selectedReport).toBeNull();

      useReportStore.getState().clearError();
      expect(useReportStore.getState().error).toBeNull();
    });
  });
});
