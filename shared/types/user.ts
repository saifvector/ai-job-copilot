import type { Profile } from './profile';
import type { Resume } from './resume';

/**
 * User entity interface matching database and API schemas
 */
export interface User {
  id: string; // UUID v4
  name: string;
  email: string;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
  profile?: Profile | null;
  resume?: Resume | null;
}

export interface CreateUserInput {
  name: string;
  email: string;
}

export interface UpdateUserInput {
  name?: string;
  email?: string;
}
