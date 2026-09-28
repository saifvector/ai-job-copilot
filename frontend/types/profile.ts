export interface Profile {
  id: string;
  userId: string;
  preferredRoles: string[];
  preferredLocations: string[];
  yearsOfExperience: number;
  resumeUrl?: string | null;
  createdAt: string;
  updatedAt: string;
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
