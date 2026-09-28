import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useResumeStore } from '../store/resume-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { Resume } from '../types/resume';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getResume: vi.fn(),
      uploadResume: vi.fn(),
      deleteResume: vi.fn(),
      downloadResume: vi.fn(),
    },
  };
});

const mockResume: Resume = {
  id: 'e0000000-0000-0000-0000-000000000001',
  userId: 'a0000000-0000-0000-0000-000000000001',
  originalFilename: 'Alex_Chen_Staff_Engineer.pdf',
  fileType: 'application/pdf',
  fileSize: 204850,
  uploadedAt: '2026-09-27T10:00:00Z',
  updatedAt: '2026-09-27T10:00:00Z',
  downloadUrl: '/api/v1/resume/download',
};

describe('useResumeStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useResumeStore.setState({
      resume: null,
      loading: false,
      uploadProgress: 0,
      error: null,
    });
  });

  it('initializes with default empty state', () => {
    const state = useResumeStore.getState();
    expect(state.resume).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.uploadProgress).toBe(0);
    expect(state.error).toBeNull();
  });

  it('fetches resume successfully', async () => {
    vi.mocked(apiClient.getResume).mockResolvedValueOnce({
      success: true,
      data: mockResume,
      timestamp: '2026-09-27T10:00:00Z',
    });

    await useResumeStore.getState().fetchResume();

    const state = useResumeStore.getState();
    expect(state.resume).toEqual(mockResume);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(apiClient.getResume).toHaveBeenCalledTimes(1);
  });

  it('handles 404 cleanly when no resume exists', async () => {
    const notFoundError = new ApiClientError('Resume not found', 404, 'RESOURCE_NOT_FOUND');
    vi.mocked(apiClient.getResume).mockRejectedValueOnce(notFoundError);

    await useResumeStore.getState().fetchResume();

    const state = useResumeStore.getState();
    expect(state.resume).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('uploads resume and records progress', async () => {
    vi.mocked(apiClient.uploadResume).mockImplementationOnce(
      async (file, onProgress) => {
        if (onProgress) {
          onProgress(50);
          onProgress(100);
        }
        return {
          success: true,
          data: mockResume,
          timestamp: '2026-09-27T10:00:00Z',
        };
      }
    );

    const testFile = new File(['%PDF-1.4 dummy content'], 'Alex_Chen.pdf', {
      type: 'application/pdf',
    });

    const success = await useResumeStore.getState().uploadResume(testFile);

    expect(success).toBe(true);
    const state = useResumeStore.getState();
    expect(state.resume).toEqual(mockResume);
    expect(state.loading).toBe(false);
    expect(state.uploadProgress).toBe(100);
    expect(state.error).toBeNull();
    expect(apiClient.uploadResume).toHaveBeenCalledWith(testFile, expect.any(Function));
  });

  it('records error and returns false when upload fails', async () => {
    const uploadErr = new ApiClientError('File exceeds 10 MB limit', 400, 'BAD_REQUEST');
    vi.mocked(apiClient.uploadResume).mockRejectedValueOnce(uploadErr);

    const testFile = new File(['too big'], 'oversized.pdf', {
      type: 'application/pdf',
    });

    const success = await useResumeStore.getState().uploadResume(testFile);

    expect(success).toBe(false);
    const state = useResumeStore.getState();
    expect(state.loading).toBe(false);
    expect(state.uploadProgress).toBe(0);
    expect(state.error).toBe('File exceeds 10 MB limit');
  });

  it('deletes active resume', async () => {
    useResumeStore.setState({ resume: mockResume });
    vi.mocked(apiClient.deleteResume).mockResolvedValueOnce({
      success: true,
      data: { success: true, message: 'Deleted' },
      timestamp: '2026-09-27T10:00:00Z',
    });

    const success = await useResumeStore.getState().deleteResume();

    expect(success).toBe(true);
    const state = useResumeStore.getState();
    expect(state.resume).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(apiClient.deleteResume).toHaveBeenCalledTimes(1);
  });

  it('clears resume and resets error via manual actions', () => {
    useResumeStore.setState({
      resume: mockResume,
      error: 'Some previous error',
      uploadProgress: 75,
    });

    useResumeStore.getState().resetError();
    expect(useResumeStore.getState().error).toBeNull();

    useResumeStore.getState().setUploadProgress(40);
    expect(useResumeStore.getState().uploadProgress).toBe(40);

    useResumeStore.getState().clearResume();
    expect(useResumeStore.getState().resume).toBeNull();
    expect(useResumeStore.getState().uploadProgress).toBe(0);
  });
});
