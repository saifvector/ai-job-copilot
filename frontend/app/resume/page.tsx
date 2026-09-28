'use client';

import * as React from 'react';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import {
  UploadCloud,
  FileText,
  Download,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  FileUp,
  ShieldCheck,
  FileType,
  HardDrive,
  Calendar,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';

import { PageHeader } from '@/components/common/page-header';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Button,
  Badge,
  Modal,
  Spinner,
} from '@/components/ui';
import { useResumeStore } from '@/store/resume-store';
import { cn, formatDate } from '@/lib/utils';

export default function ResumePage() {
  const {
    resume,
    loading,
    uploadProgress,
    error,
    fetchResume,
    uploadResume,
    deleteResume,
    downloadResume,
    resetError,
  } = useResumeStore();

  const [isDragging, setIsDragging] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [clientError, setClientError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load existing resume on mount
  useEffect(() => {
    fetchResume();
  }, [fetchResume]);

  const formatFileSize = (bytes: number): string => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const handleFileProcess = async (file: File) => {
    setClientError(null);
    setSuccessMessage(null);
    resetError();

    // Client-side pre-validations
    const validExtensions = ['.pdf', '.docx'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!validExtensions.includes(ext)) {
      setClientError('Invalid file type. Please upload a document with .pdf or .docx extension.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setClientError('File exceeds 10 MB limit. Please compress your document and try again.');
      return;
    }

    if (file.size === 0) {
      setClientError('Uploaded file is empty (0 bytes). Please select a valid document.');
      return;
    }

    const success = await uploadResume(file);
    if (success) {
      setSuccessMessage('Resume document verified and uploaded successfully.');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      await handleFileProcess(file);
    }
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      await handleFileProcess(file);
    }
  };

  const triggerBrowse = () => {
    fileInputRef.current?.click();
  };

  const confirmDelete = async () => {
    const success = await deleteResume();
    if (success) {
      setIsDeleteModalOpen(false);
      setSuccessMessage('Resume has been permanently deleted.');
    }
  };

  const activeError = clientError || error;

  return (
    <AppShell>
      <PageHeader
        title="Resume & File Management"
        description="Upload, inspect, and manage your active candidate resume."
        badge={
          <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
            Phase 2 Active
          </Badge>
        }
      />

      <div className="max-w-4xl space-y-8">
        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={handleFileInputChange}
          disabled={loading}
        />

        {/* Success Alert Banner */}
        {successMessage && (
          <div className="flex items-center justify-between rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-400 animate-fade-in">
            <div className="flex items-center space-x-3">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <span>{successMessage}</span>
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="text-xs hover:underline opacity-80"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Error Alert Banner */}
        {activeError && (
          <div className="flex items-center justify-between rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive animate-fade-in">
            <div className="flex items-center space-x-3">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>{activeError}</span>
            </div>
            <button
              onClick={() => {
                setClientError(null);
                resetError();
              }}
              className="text-xs hover:underline opacity-80"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Upload Progress Bar (Active when uploading) */}
        {loading && (
          <Card className="border-primary/40 bg-card/90 shadow-lg shadow-primary/10">
            <CardContent className="pt-6 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium flex items-center gap-2">
                  <Spinner size="sm" />
                  Uploading and inspecting document...
                </span>
                <span className="font-mono text-primary font-bold">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-muted/60 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-primary h-2.5 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Inspecting magic bytes, verifying MIME signature, and storing document.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Current Active Resume View (if uploaded) */}
        {resume && !loading && (
          <Card className="border-border/90 bg-card/80 backdrop-blur-md shadow-md">
            <CardHeader className="border-b border-border/50 pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary border border-primary/25">
                    <FileText className="h-6 w-6" />
                  </div>
                  <div>
                    <CardTitle className="text-xl font-bold flex items-center gap-2">
                      {resume.originalFilename}
                      <Badge variant="success" className="text-[10px] py-0 px-2">
                        Active
                      </Badge>
                    </CardTitle>
                    <CardDescription className="text-xs mt-1">
                      Validated and stored securely on isolated user storage.
                    </CardDescription>
                  </div>
                </div>

                <Badge variant="outline" className="font-mono text-xs uppercase">
                  {resume.fileType.includes('pdf') ? 'PDF Document' : 'Word Document'}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="pt-6">
              {/* Metadata Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 rounded-lg bg-muted/30 border border-border/60">
                <div className="space-y-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <HardDrive className="h-3.5 w-3.5" /> File Size
                  </span>
                  <p className="text-sm font-medium text-foreground">
                    {formatFileSize(resume.fileSize)}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" /> Upload Date
                  </span>
                  <p className="text-sm font-medium text-foreground">
                    {formatDate(resume.uploadedAt)}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" /> Security
                  </span>
                  <p className="text-sm font-medium text-emerald-500">MIME Verified</p>
                </div>
              </div>
            </CardContent>

            <CardFooter className="border-t border-border/40 pt-4 flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <Link href="/resume/analysis">
                  <Button variant="default" className="bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-500 shadow-sm text-white">
                    <Sparkles className="h-4 w-4 mr-2" />
                    <span>View AI Intelligence</span>
                  </Button>
                </Link>
                <Button
                  onClick={downloadResume}
                  variant="outline"
                  leftIcon={<Download className="h-4 w-4" />}
                >
                  Download
                </Button>
                <Button
                  onClick={triggerBrowse}
                  variant="outline"
                  leftIcon={<RefreshCw className="h-4 w-4" />}
                >
                  Replace
                </Button>
              </div>

              <Button
                onClick={() => setIsDeleteModalOpen(true)}
                variant="destructive"
                leftIcon={<Trash2 className="h-4 w-4" />}
              >
                Delete Resume
              </Button>
            </CardFooter>
          </Card>
        )}

        {/* Phase 3 AI Intelligence Callout Banner */}
        {resume && !loading && (
          <div className="rounded-2xl border border-primary/30 bg-gradient-to-br from-card via-card to-primary/5 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Sparkles className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
                  <span>Resume Intelligence Engine</span>
                  <Badge variant="secondary" className="text-[10px] bg-primary/10 text-primary border-primary/20">
                    Phase 3
                  </Badge>
                </h3>
                <p className="text-xs text-muted-foreground">
                  Extract structured skills, portfolio projects, career timeline, and an AI executive summary using Gemini 2.5 Pro.
                </p>
              </div>
            </div>

            <Link href="/resume/analysis" className="shrink-0">
              <Button className="gap-1.5 shadow-md hover:shadow-lg transition-all">
                <span>Open Analysis</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        )}


        {/* Drag & Drop Upload Zone (Always visible if no resume, or available for replacement) */}
        {!resume && !loading && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              'group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-200 cursor-pointer',
              isDragging
                ? 'border-primary bg-primary/10 scale-[1.01]'
                : 'border-border/80 bg-card/40 hover:border-primary/50 hover:bg-muted/20'
            )}
            onClick={triggerBrowse}
          >
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20 text-primary mb-5 group-hover:scale-110 transition-transform">
              <UploadCloud className="h-8 w-8" />
            </div>

            <h3 className="text-lg font-semibold text-foreground">
              Drag and drop your resume here
            </h3>
            <p className="mt-1 max-w-sm text-sm text-muted-foreground">
              Files are automatically inspected with magic bytes verification.
            </p>

            <div className="mt-6 flex items-center space-x-3">
              <Button
                type="button"
                variant="outline"
                size="default"
                leftIcon={<FileUp className="h-4 w-4" />}
                onClick={(e) => {
                  e.stopPropagation();
                  triggerBrowse();
                }}
              >
                Browse File
              </Button>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-4 text-xs text-muted-foreground border-t border-border/40 pt-4 w-full max-w-md">
              <div className="flex items-center gap-1.5">
                <FileType className="h-3.5 w-3.5 text-primary" />
                <span>PDF or DOCX</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-1.5">
                <HardDrive className="h-3.5 w-3.5 text-primary" />
                <span>Up to 10 MB</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                <span>Malware Protection</span>
              </div>
            </div>
          </div>
        )}

        {/* Security & Architecture Highlights */}
        <Card className="border-border/60 bg-muted/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-primary" />
              Storage Architecture & Security Controls
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground space-y-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="rounded-lg border border-border/50 bg-background/50 p-3 space-y-1">
                <span className="font-semibold text-foreground">Storage Provider Abstraction</span>
                <p>
                  Documents are stored via <code>StorageProvider</code> interface (currently <code>LocalStorageProvider</code>, ready for S3 / Cloudflare R2 / Azure / GCS).
                </p>
              </div>
              <div className="rounded-lg border border-border/50 bg-background/50 p-3 space-y-1">
                <span className="font-semibold text-foreground">Path Traversal & UUID Sharding</span>
                <p>
                  Files are partitioned into <code>uploads/resumes/&#123;user-id&#125;/&#123;uuid&#125;.ext</code>. Internal paths are never exposed to clients.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Resume Document"
        description="Are you sure you want to delete your active resume? This will purge the file from storage and clear the database record."
        footer={
          <>
            <Button variant="ghost" onClick={() => setIsDeleteModalOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete} isLoading={loading}>
              Yes, Delete Resume
            </Button>
          </>
        }
      >
        {resume && (
          <div className="rounded-lg bg-muted/50 p-3 border border-border text-xs space-y-1">
            <p className="font-medium text-foreground">Document: {resume.originalFilename}</p>
            <p className="text-muted-foreground">Size: {formatFileSize(resume.fileSize)}</p>
          </div>
        )}
      </Modal>
    </AppShell>
  );
}
