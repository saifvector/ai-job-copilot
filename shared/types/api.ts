/**
 * Standard API Response envelope
 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
  correlationId?: string;
}

/**
 * Standard Health Check Response
 */
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version?: string;
  timestamp?: string;
  uptime?: number;
  environment?: string;
  database?: {
    connected: boolean;
    latencyMs?: number;
  };
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * Paginated API Response envelope
 */
export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMeta;
}

/**
 * Standard Error details
 */
export interface ApiErrorDetail {
  loc?: (string | number)[];
  msg: string;
  type?: string;
}

export interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: ApiErrorDetail[] | Record<string, unknown>;
  };
  timestamp: string;
  correlationId?: string;
}
