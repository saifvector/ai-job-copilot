import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import type { Resume } from '../types/resume';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

const sampleResume: Resume = {
  id: 'e0000000-0000-0000-0000-000000000001',
  userId: 'a0000000-0000-0000-0000-000000000001',
  originalFilename: 'Senior_FullStack_Resume.pdf',
  fileType: 'application/pdf',
  fileSize: 1024 * 512, // 512 KB
  uploadedAt: '2026-09-27T12:00:00Z',
  updatedAt: '2026-09-27T12:00:00Z',
  downloadUrl: '/api/v1/resume/download',
};

describe('Resume Management Components', () => {
  it('renders resume metadata card with action buttons', () => {
    const onDownload = vi.fn();
    const onReplace = vi.fn();
    const onDelete = vi.fn();

    render(
      <Card data-testid="resume-card">
        <CardHeader>
          <CardTitle>{sampleResume.originalFilename}</CardTitle>
        </CardHeader>
        <CardContent>
          <div data-testid="file-type">{sampleResume.fileType}</div>
          <div data-testid="file-size">512.0 KB</div>
          <div className="flex gap-2">
            <Button onClick={onDownload}>Download</Button>
            <Button variant="outline" onClick={onReplace}>Replace</Button>
            <Button variant="destructive" onClick={onDelete}>Delete</Button>
          </div>
        </CardContent>
      </Card>
    );

    expect(screen.getByText('Senior_FullStack_Resume.pdf')).toBeDefined();
    expect(screen.getByTestId('file-type').textContent).toBe('application/pdf');
    expect(screen.getByTestId('file-size').textContent).toBe('512.0 KB');

    fireEvent.click(screen.getByText('Download'));
    expect(onDownload).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByText('Replace'));
    expect(onReplace).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByText('Delete'));
    expect(onDelete).toHaveBeenCalledTimes(1);
  });
});
