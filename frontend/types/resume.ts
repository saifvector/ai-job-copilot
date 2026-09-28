export interface Resume {
  id: string;
  userId: string;
  originalFilename: string;
  fileType: string;
  fileSize: number;
  uploadedAt: string;
  updatedAt: string;
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
