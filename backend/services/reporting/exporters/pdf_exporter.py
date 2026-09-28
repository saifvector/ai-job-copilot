"""
PDF Exporter for Phase 9 Reporting & Export Center.
Uses ReportLab to generate publication-grade executive PDF reports with
brand headers, summary cards, and structured tables.
"""
import io
import os
from typing import Any, Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas:
    """Helper can be added if needed, or simple footer flowables."""
    pass


def generate_pdf_report(data: Dict[str, Any], output_path: str) -> int:
    """
    Generate professional PDF report using ReportLab and write to output_path.
    Returns file size in bytes.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    primary_color = colors.HexColor("#4F46E5")
    dark_color = colors.HexColor("#0F172A")
    muted_color = colors.HexColor("#64748B")
    border_color = colors.HexColor("#E2E8F0")
    card_bg = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=dark_color,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=muted_color,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_color,
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_body = ParagraphStyle(
        "TableBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=dark_color,
    )

    story = []

    # 1. Header Banner & Branding
    header_data = [
        [
            Paragraph("<b>AI JOB COPILOT</b>", ParagraphStyle("Brand", fontName="Helvetica-Bold", fontSize=12, textColor=primary_color)),
            Paragraph(f"<b>Candidate:</b> {data.get('user_name', 'Alex Chen')}", ParagraphStyle("RightMeta", fontName="Helvetica", fontSize=9, alignment=2, textColor=dark_color)),
        ],
        [
            Paragraph("Career Intelligence & Autonomous Job Pipeline", ParagraphStyle("BrandSub", fontName="Helvetica", fontSize=8, textColor=muted_color)),
            Paragraph(f"Generated: {data.get('generated_at', '')}", ParagraphStyle("RightDate", fontName="Helvetica", fontSize=8, alignment=2, textColor=muted_color)),
        ],
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=4, spaceAfter=12))

    # 2. Report Main Title
    story.append(Paragraph(data.get("title", "Career Intelligence Report"), title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Comprehensive analysis and metric tracking across your active career pipeline.", subtitle_style))
    story.append(Spacer(1, 14))

    # 3. Executive Summary Cards
    summary = data.get("summary", {})
    if summary:
        story.append(Paragraph("EXECUTIVE SUMMARY", section_heading))
        summary_cells = []
        row = []
        for key, val in summary.items():
            formatted_key = key.replace("_", " ").title()
            val_str = f"{val}%" if "rate" in key or "score" in key else str(val)
            cell_p = [
                Paragraph(f"<b>{val_str}</b>", ParagraphStyle("SumVal", fontName="Helvetica-Bold", fontSize=12, textColor=primary_color, alignment=1)),
                Paragraph(formatted_key, ParagraphStyle("SumKey", fontName="Helvetica", fontSize=7.5, textColor=muted_color, alignment=1)),
            ]
            row.append(cell_p)
            if len(row) == 4:
                summary_cells.append(row)
                row = []
        if row:
            while len(row) < 4:
                row.append([Paragraph("", styles["Normal"])])
            summary_cells.append(row)

        summary_table = Table(summary_cells, colWidths=[1.75 * inch] * 4)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), card_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 16))

    # 4. Report-Specific Granular Sections
    report_type = data.get("report_type")

    # APPLICATION REPORT
    if report_type == "APPLICATION_REPORT":
        by_status = data.get("by_status", {})
        if by_status:
            story.append(Paragraph("APPLICATION PIPELINE DISTRIBUTION", section_heading))
            status_headers = [Paragraph(k, table_header) for k in by_status.keys()]
            status_values = [Paragraph(str(v), table_body) for v in by_status.values()]
            dist_table = Table([status_headers, status_values], colWidths=[1.0 * inch] * len(by_status))
            dist_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("BACKGROUND", (0, 1), (-1, 1), card_bg),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(dist_table)
            story.append(Spacer(1, 14))

        apps = data.get("applications", [])
        if apps:
            story.append(Paragraph("APPLICATION HISTORY & MILESTONES", section_heading))
            app_headers = ["Company", "Job Title", "Status", "Source", "Date Applied", "Interviews"]
            app_rows = [[Paragraph(h, table_header) for h in app_headers]]
            for a in apps[:20]:
                app_rows.append([
                    Paragraph(a.get("company", ""), table_body),
                    Paragraph(a.get("job_title", ""), table_body),
                    Paragraph(a.get("status", ""), table_body),
                    Paragraph(a.get("source", ""), table_body),
                    Paragraph(a.get("application_date") or a.get("created_at", ""), table_body),
                    Paragraph(str(a.get("interview_count", 0)), table_body),
                ])
            apps_table = Table(app_rows, colWidths=[1.3 * inch, 2.2 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch])
            apps_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(apps_table)

    # MATCH REPORT
    elif report_type == "MATCH_REPORT":
        matches = data.get("top_matches", [])
        if matches:
            story.append(Paragraph("TOP MATCH COMPATIBILITY RANKINGS", section_heading))
            m_headers = ["Company", "Role", "Overall Score", "Fit Level", "Matched Skills", "Recommendation"]
            m_rows = [[Paragraph(h, table_header) for h in m_headers]]
            for m in matches[:15]:
                m_rows.append([
                    Paragraph(m.get("company", ""), table_body),
                    Paragraph(m.get("job_title", ""), table_body),
                    Paragraph(f"<b>{m.get('overall_score', 0)}%</b>", table_body),
                    Paragraph(m.get("match_level", ""), table_body),
                    Paragraph(str(m.get("matched_skills_count", 0)), table_body),
                    Paragraph(m.get("recommendation", "")[:60] + "...", table_body),
                ])
            m_table = Table(m_rows, colWidths=[1.2 * inch, 1.8 * inch, 0.9 * inch, 0.8 * inch, 0.8 * inch, 1.5 * inch])
            m_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(m_table)
            story.append(Spacer(1, 14))

        strong = data.get("strongest_skills", [])
        weak = data.get("weakest_skills", [])
        if strong or weak:
            story.append(Paragraph("SKILL ALIGNMENT PROFILE", section_heading))
            align_headers = ["Strongest Core Competencies", "Market Skill Gaps (To Acquire)"]
            s_text = ", ".join([f"{item['skill']} ({item['frequency']}x)" for item in strong[:6]])
            w_text = ", ".join([f"{item['skill']} ({item['frequency']}x)" for item in weak[:6]])
            align_rows = [
                [Paragraph(h, table_header) for h in align_headers],
                [Paragraph(s_text, table_body), Paragraph(w_text, table_body)],
            ]
            align_table = Table(align_rows, colWidths=[3.5 * inch, 3.5 * inch])
            align_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("BACKGROUND", (0, 1), (-1, 1), card_bg),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(align_table)

    # SKILL REPORT
    elif report_type == "SKILL_REPORT":
        priorities = data.get("priorities", [])
        if priorities:
            story.append(Paragraph("PRIORITY SKILL ACQUISITION ROADMAP", section_heading))
            p_headers = ["Priority", "Target Skill", "Urgency Tier", "Job Demand", "Est. Weeks", "Action Plan"]
            p_rows = [[Paragraph(h, table_header) for h in p_headers]]
            for p in priorities:
                p_rows.append([
                    Paragraph(f"<b>Priority {p.get('priority')}</b>", table_body),
                    Paragraph(p.get("skill", ""), table_body),
                    Paragraph(p.get("importance", ""), table_body),
                    Paragraph(f"{p.get('job_demand_count', 0)} jobs", table_body),
                    Paragraph(f"{p.get('estimated_weeks', 2)} wks", table_body),
                    Paragraph(p.get("suggested_action", ""), table_body),
                ])
            p_table = Table(p_rows, colWidths=[0.9 * inch, 1.1 * inch, 1.2 * inch, 0.8 * inch, 0.7 * inch, 2.3 * inch])
            p_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(p_table)
            story.append(Spacer(1, 14))

        roadmap = data.get("suggested_roadmap", [])
        if roadmap:
            story.append(Paragraph("EXECUTION SPRINTS", section_heading))
            r_headers = ["Sprint", "Primary Technology", "Sprint Goal & Deliverables"]
            r_rows = [[Paragraph(h, table_header) for h in r_headers]]
            for r in roadmap:
                r_rows.append([
                    Paragraph(r.get("phase", ""), table_body),
                    Paragraph(r.get("focus", ""), table_body),
                    Paragraph(r.get("goal", ""), table_body),
                ])
            r_table = Table(r_rows, colWidths=[1.5 * inch, 1.5 * inch, 4.0 * inch])
            r_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(r_table)

    # CAREER REPORT
    elif report_type == "CAREER_REPORT":
        dims = data.get("readiness_dimensions", {})
        if dims:
            story.append(Paragraph("CAREER READINESS PILLARS", section_heading))
            d_headers = [Paragraph(k, table_header) for k in dims.keys()]
            d_vals = [Paragraph(f"<b>{v}%</b>", table_body) for v in dims.values()]
            d_table = Table([d_headers, d_vals], colWidths=[1.75 * inch] * len(dims))
            d_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("BACKGROUND", (0, 1), (-1, 1), card_bg),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(d_table)
            story.append(Spacer(1, 14))

        recs = data.get("recommendations", [])
        if recs:
            story.append(Paragraph("STRATEGIC RECOMMENDATIONS", section_heading))
            for i, rec in enumerate(recs, 1):
                story.append(Paragraph(f"<b>{i}.</b> {rec}", body_style))
                story.append(Spacer(1, 4))
            story.append(Spacer(1, 10))

    # RESUME REPORT
    elif report_type == "RESUME_REPORT":
        history = data.get("tailoring_history", [])
        if history:
            story.append(Paragraph("TAILORING HISTORY & ATS VERIFICATION", section_heading))
            th_headers = ["Company", "Target Role", "ATS Score", "Target Match", "Date Generated"]
            th_rows = [[Paragraph(h, table_header) for h in th_headers]]
            for th in history[:15]:
                th_rows.append([
                    Paragraph(th.get("target_company", ""), table_body),
                    Paragraph(th.get("target_role", ""), table_body),
                    Paragraph(f"<b>{th.get('ats_score', 0)}/100</b>", table_body),
                    Paragraph(f"{th.get('target_match_score', 0)}%", table_body),
                    Paragraph(th.get("created_at", ""), table_body),
                ])
            th_table = Table(th_rows, colWidths=[1.5 * inch, 2.3 * inch, 1.1 * inch, 1.1 * inch, 1.0 * inch])
            th_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), dark_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(th_table)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=10, spaceAfter=8))
    story.append(Paragraph("Generated automatically by AI Job Copilot • Career Discovery, Matching, and Automation Engine", subtitle_style))

    doc.build(story)
    return os.path.getsize(output_path)
