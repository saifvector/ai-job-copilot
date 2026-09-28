/**
 * Resume entity interface matching backend API schemas
 */
export interface Resume {
  id: string; // UUID v4
  userId: string; // UUID v4
  originalFilename: string;
  fileType: string;
  fileSize: number; // in bytes
  uploadedAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
  downloadUrl: string;
}

export interface ResumeUploadResponse {
  success: boolean;
  data: Resume;
  message?: string;
  timestamp: string;
}

export interface ResumeDeleteResponse {
  success: boolean;
  message: string;
}
