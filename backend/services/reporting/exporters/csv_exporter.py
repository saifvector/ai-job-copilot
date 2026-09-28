"""
CSV Exporter for Phase 9 Reporting & Export Center.
Generates standard RFC 4180 CSV exports for applications, matches,
skills, and career metrics.
"""
import csv
import os
from typing import Any, Dict


def generate_csv_report(data: Dict[str, Any], output_path: str) -> int:
    """
    Generate CSV export file based on report type and data payload.
    Returns file size in bytes.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report_type = data.get("report_type")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # File metadata banner
        writer.writerow(["# AI JOB COPILOT REPORT EXPORT"])
        writer.writerow(["# Title", data.get("title", "Report")])
        writer.writerow(["# Candidate", data.get("user_name", "Alex Chen")])
        writer.writerow(["# Generated At", data.get("generated_at", "")])
        writer.writerow([])

        if report_type == "APPLICATION_REPORT":
            # Summary metrics
            summary = data.get("summary", {})
            writer.writerow(["METRIC", "VALUE"])
            for k, v in summary.items():
                writer.writerow([k.replace("_", " ").title(), v])
            writer.writerow([])

            # Detailed Applications Table
            writer.writerow(["APPLICATIONS DETAIL"])
            writer.writerow(["Company", "Job Title", "Location", "Status", "Source", "Date Applied", "Interviews", "Notes"])
            for app in data.get("applications", []):
                writer.writerow([
                    app.get("company", ""),
                    app.get("job_title", ""),
                    app.get("location", ""),
                    app.get("status", ""),
                    app.get("source", ""),
                    app.get("application_date") or app.get("created_at", ""),
                    app.get("interview_count", 0),
                    app.get("notes", ""),
                ])

        elif report_type == "MATCH_REPORT":
            summary = data.get("summary", {})
            writer.writerow(["METRIC", "VALUE"])
            for k, v in summary.items():
                writer.writerow([k.replace("_", " ").title(), v])
            writer.writerow([])

            writer.writerow(["JOB MATCH RANKINGS"])
            writer.writerow(["Company", "Role", "Overall Score", "Fit Level", "Skill Score", "Experience Score", "Recommendation"])
            for m in data.get("top_matches", []):
                writer.writerow([
                    m.get("company", ""),
                    m.get("job_title", ""),
                    f"{m.get('overall_score', 0)}%",
                    m.get("match_level", ""),
                    f"{m.get('skill_score', 0)}%",
                    f"{m.get('experience_score', 0)}%",
                    m.get("recommendation", ""),
                ])

        elif report_type == "SKILL_REPORT":
            summary = data.get("summary", {})
            writer.writerow(["METRIC", "VALUE"])
            for k, v in summary.items():
                writer.writerow([k.replace("_", " ").title(), v])
            writer.writerow([])

            writer.writerow(["PRIORITY SKILLS TO ACQUIRE"])
            writer.writerow(["Priority", "Skill", "Importance", "Job Demand Count", "Est. Weeks", "Action Plan"])
            for p in data.get("priorities", []):
                writer.writerow([
                    p.get("priority", 1),
                    p.get("skill", ""),
                    p.get("importance", ""),
                    p.get("job_demand_count", 0),
                    p.get("estimated_weeks", 2),
                    p.get("suggested_action", ""),
                ])

        elif report_type == "CAREER_REPORT":
            summary = data.get("summary", {})
            writer.writerow(["METRIC", "VALUE"])
            for k, v in summary.items():
                writer.writerow([k.replace("_", " ").title(), v])
            writer.writerow([])

            writer.writerow(["READINESS DIMENSIONS"])
            for k, v in data.get("readiness_dimensions", {}).items():
                writer.writerow([k, f"{v}%"])
            writer.writerow([])

            writer.writerow(["RECOMMENDATIONS"])
            for i, rec in enumerate(data.get("recommendations", []), 1):
                writer.writerow([f"Action {i}", rec])

        elif report_type == "RESUME_REPORT":
            summary = data.get("summary", {})
            writer.writerow(["METRIC", "VALUE"])
            for k, v in summary.items():
                writer.writerow([k.replace("_", " ").title(), v])
            writer.writerow([])

            writer.writerow(["TAILORING HISTORY"])
            writer.writerow(["Company", "Target Role", "ATS Score", "Target Match Score", "Date Generated"])
            for th in data.get("tailoring_history", []):
                writer.writerow([
                    th.get("target_company", ""),
                    th.get("target_role", ""),
                    th.get("ats_score", 0),
                    f"{th.get('target_match_score', 0)}%",
                    th.get("created_at", ""),
                ])

    return os.path.getsize(output_path)
