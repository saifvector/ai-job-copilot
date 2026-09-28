export const APP_CONFIG = {
  NAME: 'AI Job Copilot',
  VERSION: '0.1.0',
  DESCRIPTION: 'Intelligent Career Agent and Automated Job Application Assistant',
  DEFAULT_LOCALE: 'en-US',
  DEFAULT_THEME: 'dark',
} as const;

export const API_ROUTES = {
  HEALTH: '/health',
  V1: {
    PREFIX: '/api/v1',
    HEALTH: '/api/v1/health',
    USERS: '/api/v1/users',
    PROFILES: '/api/v1/profiles',
  },
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
} as const;

export const PAGINATION_DEFAULTS = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
} as const;
