import React from 'react';
import { FolderGit2, Tag } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Project } from '@/types';

interface ProjectsSectionProps {
  projects: Project[];
}

export const ProjectsSection: React.FC<ProjectsSectionProps> = ({ projects }) => {
  return (
    <Card className="border border-border/80 bg-card/60 backdrop-blur-md shadow-sm transition-all hover:border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-500">
            <FolderGit2 className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base md:text-lg font-semibold flex items-center gap-2">
              <span>Key Projects & Portfolio</span>
              <span className="text-xs font-normal text-muted-foreground">
                ({projects.length})
              </span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Technical initiatives, system architectures, and practical applications
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {projects.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No projects extracted from resume.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((project, idx) => (
              <div
                key={project.id || `${project.title}-${idx}`}
                className="flex flex-col justify-between p-4 rounded-xl border border-border/60 bg-muted/20 hover:border-border transition-all"
              >
                <div className="space-y-2">
                  <h4 className="text-base font-semibold text-foreground tracking-tight">
                    {project.title}
                  </h4>
                  {project.description && (
                    <p className="text-xs md:text-sm text-muted-foreground leading-relaxed">
                      {project.description}
                    </p>
                  )}
                </div>

                {project.technologies && project.technologies.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-border/40 flex flex-wrap items-center gap-1.5">
                    <Tag className="h-3 w-3 text-muted-foreground mr-0.5" />
                    {project.technologies.map((tech) => (
                      <Badge
                        key={tech}
                        variant="secondary"
                        className="text-[11px] px-2 py-0.5 bg-muted text-muted-foreground"
                      >
                        {tech}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
