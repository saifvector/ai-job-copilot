'use client';

import React, { useState } from 'react';
import { Experience, ResumeVersion, TailoredResume } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useProfileStore } from '@/store';
import {
  FileText,
  Sparkles,
  ArrowRight,
  Columns,
  Maximize2,
  CheckCircle2,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Award,
} from 'lucide-react';

interface VersionComparisonViewProps {
  tailoredResume: TailoredResume;
  activeVersionKey: 'ats' | 'recruiter' | 'balanced';
  onSelectVersion: (version: 'ats' | 'recruiter' | 'balanced') => void;
  className?: string;
}

export const VersionComparisonView: React.FC<VersionComparisonViewProps> = ({
  tailoredResume,
  activeVersionKey,
  onSelectVersion,
  className = '',
}) => {
  const [viewMode, setViewMode] = useState<'comparison' | 'preview'>('comparison');
  const { profile, skills: origSkills, experience: origExperiences } = useProfileStore();
  const origSummary = profile?.summary || '';

  const versions = tailoredResume.versions || {};
  const activeVersion: ResumeVersion | undefined =
    versions[activeVersionKey] || versions['balanced'] || Object.values(versions)[0];

  if (!activeVersion) {
    return (
      <div className="p-8 text-center text-muted-foreground border rounded-xl">
        No version content available for display.
      </div>
    );
  }

  const matchedKeywordsLower = new Set(
    (tailoredResume.keywordAnalysis?.matchedKeywords || []).map((k) => k.toLowerCase())
  );

  // Helper to render text with keyword highlights
  const renderHighlightedText = (text: string, highlightKeywords: string[] = []) => {
    if (!text) return null;
    const allKeywords = new Set([
      ...highlightKeywords.map((k) => k.toLowerCase()),
      ...matchedKeywordsLower,
    ]);

    // Simple word scanner for highlight demonstration
    const words = text.split(/(\s+|[.,;!?()]+)/);
    return (
      <span>
        {words.map((word, i) => {
          const cleanWord = word.trim().toLowerCase();
          if (allKeywords.has(cleanWord) && cleanWord.length > 2) {
            return (
              <mark
                key={i}
                className="bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-semibold px-1 py-0.5 rounded text-[11px]"
              >
                {word}
              </mark>
            );
          }
          return <span key={i}>{word}</span>;
        })}
      </span>
    );
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Version Selector Tabs & View Mode Switch */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/50 pb-3">
        {/* Version Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-muted/40 rounded-xl border border-border/40 overflow-x-auto">
          {(['balanced', 'ats', 'recruiter'] as const).map((key) => {
            const v = versions[key];
            const isSelected = activeVersionKey === key;
            const label =
              key === 'ats'
                ? 'Version A: ATS'
                : key === 'recruiter'
                ? 'Version B: Recruiter'
                : 'Version C: Balanced';

            return (
              <button
                key={key}
                onClick={() => onSelectVersion(key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all shrink-0 ${
                  isSelected
                    ? 'bg-background text-foreground shadow-sm font-semibold'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-muted/40 p-1 rounded-xl border border-border/40">
            <Button
              variant={viewMode === 'comparison' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('comparison')}
              className="h-7 text-xs px-2.5 gap-1.5"
            >
              <Columns className="w-3.5 h-3.5" />
              Side-by-Side
            </Button>
            <Button
              variant={viewMode === 'preview' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('preview')}
              className="h-7 text-xs px-2.5 gap-1.5"
            >
              <Maximize2 className="w-3.5 h-3.5" />
              Full Preview
            </Button>
          </div>
        </div>
      </div>

      {/* Highlights Legend */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground px-2">
        <span className="font-semibold text-foreground">Highlights:</span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-emerald-500/80 inline-block" />
          Targeted Keywords Matched
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-blue-500/80 inline-block" />
          Optimized Bullet Points
        </span>
      </div>

      {/* Main Content Area */}
      {viewMode === 'comparison' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Left Column: Original Profile */}
          <Card className="border border-border/60 shadow-sm bg-muted/10">
            <CardHeader className="pb-3 border-b border-border/40 bg-muted/30">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold flex items-center gap-2 text-muted-foreground">
                  <FileText className="w-4 h-4" />
                  Original Resume Baseline
                </CardTitle>
                <Badge variant="outline" className="text-[11px] font-normal">
                  Verified Baseline
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-4 space-y-6 text-xs leading-relaxed">
              {/* Summary */}
              <div className="space-y-1.5">
                <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-muted-foreground">
                  Professional Summary
                </h4>
                <p className="text-muted-foreground bg-muted/20 p-3 rounded-lg border border-border/40">
                  {origSummary || 'No candidate summary provided in original profile.'}
                </p>
              </div>

              {/* Skills */}
              <div className="space-y-1.5">
                <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-muted-foreground">
                  Verified Skills ({origSkills?.length || 0})
                </h4>
                <div className="flex flex-wrap gap-1 bg-muted/20 p-3 rounded-lg border border-border/40">
                  {origSkills && origSkills.length > 0 ? (
                    origSkills.map((s) => (
                      <Badge key={s.id || s.name} variant="outline" className="text-[11px] font-normal">
                        {s.name}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-muted-foreground italic">No verified skills stored</span>
                  )}
                </div>
              </div>

              {/* Experience */}
              <div className="space-y-2">
                <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-muted-foreground">
                  Documented Experience ({origExperiences?.length || 0})
                </h4>
                <div className="space-y-3">
                  {origExperiences && origExperiences.length > 0 ? (
                    origExperiences.map((exp: Experience) => (
                      <div key={exp.id} className="p-3 bg-muted/20 rounded-lg border border-border/40 space-y-1">
                        <div className="font-semibold text-foreground">
                          {exp.role} — <span className="text-muted-foreground font-normal">{exp.company}</span>
                        </div>
                        <p className="text-muted-foreground line-clamp-3">{exp.description}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 bg-muted/20 rounded-lg border border-border/40 text-muted-foreground italic">
                      No experience records stored
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Right Column: Tailored Version */}
          <Card className="border border-primary/30 shadow-md bg-background relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-blue-500 to-emerald-500" />
            <CardHeader className="pb-3 border-b border-border/40 bg-primary/5">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold flex items-center gap-2 text-foreground">
                  <Sparkles className="w-4 h-4 text-primary" />
                  {activeVersion.label}
                </CardTitle>
                <div className="flex items-center gap-1.5">
                  <Badge variant="outline" className="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800 text-[11px] font-semibold">
                    ATS Score: {Math.round(tailoredResume.atsScore)}%
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-4 space-y-6 text-xs leading-relaxed">
              {/* Summary */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-primary">
                    Tailored Professional Summary
                  </h4>
                  <Badge variant="outline" className="text-[10px] text-primary border-primary/30">
                    Keyword Aligned
                  </Badge>
                </div>
                <div className="p-3 rounded-lg border border-primary/20 bg-primary/5 text-foreground leading-relaxed">
                  {renderHighlightedText(activeVersion.summary)}
                </div>
              </div>

              {/* Core Skills Categorized */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-primary">
                    Targeted Skill Grouping
                  </h4>
                  <span className="text-[11px] text-muted-foreground">
                    Grouped for ATS Scanners
                  </span>
                </div>
                <div className="space-y-2">
                  {activeVersion.skills.map((group) => (
                    <div key={group.category} className="p-2.5 rounded-lg border border-border/50 bg-muted/20 space-y-1">
                      <div className="text-[11px] font-semibold text-foreground flex items-center gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                        {group.category}
                      </div>
                      <div className="flex flex-wrap gap-1 pt-0.5">
                        {group.skills.map((s) => {
                          const isMatched = matchedKeywordsLower.has(s.toLowerCase());
                          return (
                            <Badge
                              key={s}
                              variant="outline"
                              className={`text-[11px] font-normal py-0.5 ${
                                isMatched
                                  ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800 font-medium'
                                  : 'bg-muted/40 text-muted-foreground border-border/50'
                              }`}
                            >
                              {s}
                            </Badge>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Work Experience */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-primary flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5 text-primary" />
                    Impact-Driven Work Experience
                  </h4>
                  <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                    Active Verbs + Metrics
                  </span>
                </div>
                <div className="space-y-3.5">
                  {activeVersion.experience.map((exp, idx) => (
                    <div key={exp.id || idx} className="p-3.5 rounded-lg border border-border/60 bg-muted/10 space-y-2">
                      <div className="flex items-baseline justify-between flex-wrap gap-1">
                        <div className="font-bold text-foreground text-sm">
                          {exp.role}{' '}
                          <span className="text-primary font-normal text-xs">@ {exp.company}</span>
                        </div>
                        {(exp.startDate || exp.endDate) && (
                          <span className="text-[11px] text-muted-foreground italic">
                            {exp.startDate} – {exp.endDate}
                          </span>
                        )}
                      </div>
                      {exp.description && (
                        <p className="text-muted-foreground text-xs italic">
                          {exp.description}
                        </p>
                      )}
                      <ul className="space-y-1.5 pt-1 pl-1">
                        {exp.bulletPoints.map((bullet, bIdx) => (
                          <li key={bIdx} className="flex items-start gap-2 text-xs leading-relaxed text-foreground">
                            <span className="text-primary mt-1">•</span>
                            <div>{renderHighlightedText(bullet, exp.highlightedKeywords)}</div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Projects */}
              {activeVersion.projects.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-border/40">
                  <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-primary flex items-center gap-1.5">
                    <FolderGit2 className="w-3.5 h-3.5 text-primary" />
                    Technical Projects
                  </h4>
                  <div className="space-y-2">
                    {activeVersion.projects.map((proj, pIdx) => (
                      <div key={proj.id || pIdx} className="p-3 rounded-lg border border-border/50 bg-muted/10 space-y-1">
                        <div className="font-semibold text-foreground text-xs flex items-center justify-between">
                          <span>{proj.title}</span>
                          {proj.technologies && proj.technologies.length > 0 && (
                            <span className="text-[10px] text-muted-foreground font-normal">
                              {proj.technologies.join(', ')}
                            </span>
                          )}
                        </div>
                        <p className="text-muted-foreground text-xs">{proj.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education & Certifications */}
              {(activeVersion.education.length > 0 || activeVersion.certifications.length > 0) && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-border/40">
                  {activeVersion.education.length > 0 && (
                    <div className="space-y-1.5">
                      <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-primary flex items-center gap-1.5">
                        <GraduationCap className="w-3.5 h-3.5" />
                        Education
                      </h4>
                      {activeVersion.education.map((edu, eIdx) => (
                        <div key={edu.id || eIdx} className="p-2.5 rounded-lg border border-border/40 bg-muted/10 text-xs">
                          <div className="font-semibold text-foreground">{edu.degree}</div>
                          <div className="text-muted-foreground text-[11px]">{edu.institution}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeVersion.certifications.length > 0 && (
                    <div className="space-y-1.5">
                      <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] text-primary flex items-center gap-1.5">
                        <Award className="w-3.5 h-3.5" />
                        Certifications
                      </h4>
                      {activeVersion.certifications.map((cert, cIdx) => (
                        <div key={cert.id || cIdx} className="p-2.5 rounded-lg border border-border/40 bg-muted/10 text-xs">
                          <div className="font-semibold text-foreground">{cert.name}</div>
                          <div className="text-muted-foreground text-[11px]">{cert.issuer}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Full Document Preview View */
        <Card className="border border-border/80 shadow-md max-w-4xl mx-auto bg-card">
          <CardContent className="p-8 sm:p-12 space-y-6 font-sans">
            {/* Header */}
            <div className="border-b border-border/60 pb-5 text-center space-y-1">
              <h2 className="text-2xl font-bold tracking-tight text-foreground">
                {tailoredResume.title}
              </h2>
              <p className="text-xs text-muted-foreground">
                Job Tailored Edition &bull; ATS Score: {Math.round(tailoredResume.atsScore)}% &bull; Keyword Coverage: {Math.round(tailoredResume.keywordCoverage)}%
              </p>
            </div>

            {/* Summary */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-primary border-b border-border/40 pb-1">
                Professional Summary
              </h3>
              <p className="text-sm leading-relaxed text-foreground">
                {renderHighlightedText(activeVersion.summary)}
              </p>
            </div>

            {/* Core Competencies */}
            {activeVersion.skills.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-primary border-b border-border/40 pb-1">
                  Core Competencies & Technical Skills
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  {activeVersion.skills.map((group) => (
                    <div key={group.category} className="space-y-0.5">
                      <span className="font-semibold text-foreground text-xs">{group.category}: </span>
                      <span className="text-muted-foreground text-xs">{group.skills.join(', ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Experience */}
            {activeVersion.experience.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-primary border-b border-border/40 pb-1">
                  Professional Experience
                </h3>
                <div className="space-y-4">
                  {activeVersion.experience.map((exp, idx) => (
                    <div key={exp.id || idx} className="space-y-1.5">
                      <div className="flex items-baseline justify-between text-sm flex-wrap">
                        <span className="font-bold text-foreground">
                          {exp.role} <span className="font-normal text-muted-foreground">— {exp.company}</span>
                        </span>
                        <span className="text-xs text-muted-foreground italic">
                          {exp.startDate} – {exp.endDate}
                        </span>
                      </div>
                      <ul className="space-y-1 pl-4 list-disc text-xs text-foreground leading-relaxed">
                        {exp.bulletPoints.map((bullet, bIdx) => (
                          <li key={bIdx}>{renderHighlightedText(bullet, exp.highlightedKeywords)}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {activeVersion.education.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-primary border-b border-border/40 pb-1">
                  Education
                </h3>
                <div className="space-y-2 text-xs">
                  {activeVersion.education.map((edu, eIdx) => (
                    <div key={edu.id || eIdx} className="flex justify-between">
                      <span className="font-semibold text-foreground">
                        {edu.degree} {edu.fieldOfStudy ? `in ${edu.fieldOfStudy}` : ''} — {edu.institution}
                      </span>
                      <span className="text-muted-foreground italic">
                        {edu.startDate} – {edu.endDate}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
