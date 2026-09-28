import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTaskStore } from '../store/task-store';
import { apiClient } from '../services/api-client';
import type { AgentTask } from '../types/agent';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      listTasks: vi.fn(),
      getTask: vi.fn(),
      createTask: vi.fn(),
      retryTask: vi.fn(),
      cancelTask: vi.fn(),
    },
  };
});

const mockTask: AgentTask = {
  id: 'task-100',
  agent: 'JobDiscoveryAgent',
  status: 'PENDING',
  payload: { query: 'DevOps Engineer' },
  result: null,
  error_message: null,
  model_used: 'gemini-2.5-flash',
  duration_ms: null,
  retry_count: 0,
  max_retries: 3,
  created_at: '2026-09-28T12:00:00Z',
  updated_at: '2026-09-28T12:00:00Z',
  completed_at: null,
};

describe('useTaskStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useTaskStore.setState({
      tasks: [],
      selectedTask: null,
      filterStatus: null,
      filterAgent: null,
      loading: false,
      actionLoading: false,
      error: null,
    });
  });

  it('fetches tasks and assigns default selected task', async () => {
    vi.mocked(apiClient.listTasks).mockResolvedValueOnce({
      items: [mockTask],
      total: 1,
    });

    await useTaskStore.getState().fetchTasks();

    const state = useTaskStore.getState();
    expect(state.tasks).toHaveLength(1);
    expect(state.tasks[0].id).toBe('task-100');
    expect(state.selectedTask?.id).toBe('task-100');
  });

  it('enqueues a new background agent task', async () => {
    vi.mocked(apiClient.createTask).mockResolvedValueOnce(mockTask);

    const task = await useTaskStore.getState().createTask('JobDiscoveryAgent', { query: 'DevOps Engineer' });

    expect(task).toEqual(mockTask);
    expect(useTaskStore.getState().tasks).toContainEqual(mockTask);
  });

  it('retries a failed task', async () => {
    const retriedTask: AgentTask = {
      ...mockTask,
      retry_count: 1,
      status: 'PENDING',
    };
    useTaskStore.setState({ tasks: [mockTask], selectedTask: mockTask });
    vi.mocked(apiClient.retryTask).mockResolvedValueOnce(retriedTask);

    const ok = await useTaskStore.getState().retryTask('task-100');

    expect(ok).toBe(true);
    expect(useTaskStore.getState().tasks[0].retry_count).toBe(1);
  });

  it('cancels a running/pending task', async () => {
    const cancelledTask: AgentTask = {
      ...mockTask,
      status: 'CANCELLED',
    };
    useTaskStore.setState({ tasks: [mockTask], selectedTask: mockTask });
    vi.mocked(apiClient.cancelTask).mockResolvedValueOnce(cancelledTask);

    const ok = await useTaskStore.getState().cancelTask('task-100');

    expect(ok).toBe(true);
    expect(useTaskStore.getState().tasks[0].status).toBe('CANCELLED');
  });
});
