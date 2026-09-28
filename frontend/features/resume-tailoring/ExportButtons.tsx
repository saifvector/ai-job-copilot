'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Download, FileText, FileCode, File, Loader2 } from 'lucide-react';
import { useTailoredResumeStore } from '@/store';

interface ExportButtonsProps {
  className?: string;
  version?: 'ats' | 'recruiter' | 'balanced';
}

export const ExportButtons: React.FC<ExportButtonsProps> = ({
  className = '',
  version,
}) => {
  const { exportResume, exporting, selectedResume } = useTailoredResumeStore();
  const [activeFormat, setActiveFormat] = useState<string | null>(null);

  if (!selectedResume) return null;

  const handleExport = async (format: 'pdf' | 'docx' | 'markdown') => {
    setActiveFormat(format);
    await exportResume(format, version);
    setActiveFormat(null);
  };

  return (
    <div className={`flex items-center gap-2 flex-wrap ${className}`}>
      {/* Export as PDF */}
      <Button
        variant="default"
        size="sm"
        disabled={exporting}
        onClick={() => handleExport('pdf')}
        className="gap-2 text-xs font-medium"
      >
        {exporting && activeFormat === 'pdf' ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <File className="w-3.5 h-3.5 text-red-300" />
        )}
        Download PDF
      </Button>

      {/* Export as DOCX */}
      <Button
        variant="outline"
        size="sm"
        disabled={exporting}
        onClick={() => handleExport('docx')}
        className="gap-2 text-xs font-medium"
      >
        {exporting && activeFormat === 'docx' ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <FileText className="w-3.5 h-3.5 text-blue-500" />
        )}
        Download DOCX
      </Button>

      {/* Export as Markdown */}
      <Button
        variant="outline"
        size="sm"
        disabled={exporting}
        onClick={() => handleExport('markdown')}
        className="gap-2 text-xs font-medium"
      >
        {exporting && activeFormat === 'markdown' ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <FileCode className="w-3.5 h-3.5 text-emerald-500" />
        )}
        Download Markdown
      </Button>
    </div>
  );
};
