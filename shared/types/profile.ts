/**
 * Profile entity interface matching database and API schemas
 */
export interface Profile {
  id: string; // UUID v4
  userId: string; // UUID v4 Foreign Key
  preferredRoles: string[];
  preferredLocations: string[];
  yearsOfExperience: number;
  resumeUrl?: string | null;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
}

export interface CreateProfileInput {
  userId: string;
  preferredRoles?: string[];
  preferredLocations?: string[];
  yearsOfExperience?: number;
  resumeUrl?: string | null;
}

export interface UpdateProfileInput {
  preferredRoles?: string[];
  preferredLocations?: string[];
  yearsOfExperience?: number;
  resumeUrl?: string | null;
}
