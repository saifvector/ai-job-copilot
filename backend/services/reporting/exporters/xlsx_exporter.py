"""
XLSX Exporter for Phase 9 Reporting & Export Center.
Uses openpyxl to generate styled multi-sheet Excel workbooks with
Applications, Matches, and Analytics tabs.
"""
import os
from typing import Any, Dict
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


def generate_xlsx_report(
    data: Dict[str, Any],
    all_context: Dict[str, Any],
    output_path: str,
) -> int:
    """
    Generate professional multi-tab XLSX spreadsheet and write to output_path.
    Sheets: Applications, Matches, Analytics.
    Returns file size in bytes.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()

    # Brand Styling definitions
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    title_font = Font(name="Calibri", size=14, bold=True, color="4F46E5")
    subtitle_font = Font(name="Calibri", size=9, italic=True, color="64748B")
    metric_title_font = Font(name="Calibri", size=10, bold=True, color="0F172A")
    metric_val_font = Font(name="Calibri", size=11, bold=True, color="4F46E5")

    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0"),
    )

    # 1. SHEET: Applications
    ws_apps = wb.active
    ws_apps.title = "Applications"
    ws_apps.views.sheetView[0].showGridLines = True

    # Title block
    ws_apps["A1"] = "AI Job Copilot — Applications Pipeline"
    ws_apps["A1"].font = title_font
    ws_apps["A2"] = f"Candidate: {data.get('user_name', 'Alex Chen')} | Exported: {data.get('generated_at', '')}"
    ws_apps["A2"].font = subtitle_font

    app_headers = ["Company", "Job Title", "Location", "Status", "Source", "Date Applied", "Interviews", "Notes"]
    for col_idx, h in enumerate(app_headers, 1):
        cell = ws_apps.cell(row=4, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center" if h in ["Status", "Interviews", "Date Applied"] else "left")

    apps_list = all_context.get("applications", data.get("applications", []))
    for row_idx, app in enumerate(apps_list, 5):
        row_vals = [
            app.get("company", ""),
            app.get("job_title", ""),
            app.get("location", ""),
            app.get("status", ""),
            app.get("source", ""),
            app.get("application_date") or app.get("created_at", ""),
            app.get("interview_count", 0),
            app.get("notes", ""),
        ]
        is_even = (row_idx % 2 == 0)
        for col_idx, val in enumerate(row_vals, 1):
            c = ws_apps.cell(row=row_idx, column=col_idx, value=val)
            c.border = thin_border
            if is_even:
                c.fill = zebra_fill
            if col_idx in [4, 6, 7]:
                c.alignment = Alignment(horizontal="center")

    # 2. SHEET: Matches
    ws_matches = wb.create_sheet(title="Matches")
    ws_matches.views.sheetView[0].showGridLines = True

    ws_matches["A1"] = "AI Job Copilot — Job Match Compatibility"
    ws_matches["A1"].font = title_font
    ws_matches["A2"] = f"Candidate: {data.get('user_name', 'Alex Chen')} | Exported: {data.get('generated_at', '')}"
    ws_matches["A2"].font = subtitle_font

    match_headers = ["Company", "Position Role", "Overall Score", "Fit Tier", "Skill Score", "Experience Score", "Matched Skills", "Missing Skills", "Recommendation"]
    for col_idx, h in enumerate(match_headers, 1):
        cell = ws_matches.cell(row=4, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center" if "Score" in h or h == "Fit Tier" else "left")

    matches_list = all_context.get("matches", data.get("top_matches", []))
    for row_idx, m in enumerate(matches_list, 5):
        m_vals = [
            m.get("company", ""),
            m.get("job_title", ""),
            f"{m.get('overall_score', 0)}%",
            m.get("match_level", ""),
            f"{m.get('skill_score', 0)}%",
            f"{m.get('experience_score', 0)}%",
            m.get("matched_skills_count", 0),
            m.get("missing_skills_count", 0),
            m.get("recommendation", ""),
        ]
        is_even = (row_idx % 2 == 0)
        for col_idx, val in enumerate(m_vals, 1):
            c = ws_matches.cell(row=row_idx, column=col_idx, value=val)
            c.border = thin_border
            if is_even:
                c.fill = zebra_fill
            if col_idx in [3, 4, 5, 6, 7, 8]:
                c.alignment = Alignment(horizontal="center")

    # 3. SHEET: Analytics
    ws_analytics = wb.create_sheet(title="Analytics")
    ws_analytics.views.sheetView[0].showGridLines = True

    ws_analytics["A1"] = "AI Job Copilot — Career Analytics & Metrics"
    ws_analytics["A1"].font = title_font
    ws_analytics["A2"] = f"Candidate: {data.get('user_name', 'Alex Chen')} | Exported: {data.get('generated_at', '')}"
    ws_analytics["A2"].font = subtitle_font

    # Overview Metrics Table
    ws_analytics["A4"] = "Conversion & Funnel Metrics"
    ws_analytics["A4"].font = metric_title_font
    analytics_headers = ["Metric Category", "Calculated Value", "Benchmark Target", "Status"]
    for col_idx, h in enumerate(analytics_headers, 1):
        cell = ws_analytics.cell(row=5, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill

    summary_data = all_context.get("summary", data.get("summary", {}))
    metrics_rows = [
        ("Total Applications Tracked", summary_data.get("total_applications", 0), "N/A", "Active"),
        ("Applications Sent", summary_data.get("applications_sent", 0), "> 10 / month", "Good"),
        ("Interviews Reached", summary_data.get("interviews_reached", 0), "> 20%", "Tracking"),
        ("Response Rate %", f"{summary_data.get('response_rate', 0)}%", "> 25%", "Healthy" if summary_data.get("response_rate", 0) >= 20 else "Needs Optimization"),
        ("Interview Rate %", f"{summary_data.get('interview_rate', 0)}%", "> 15%", "Strong" if summary_data.get("interview_rate", 0) >= 15 else "Targeted"),
        ("Offer Rate %", f"{summary_data.get('offer_rate', 0)}%", "> 5%", "On Track"),
    ]

    for row_idx, (m_name, m_val, m_target, m_stat) in enumerate(metrics_rows, 6):
        c1 = ws_analytics.cell(row=row_idx, column=1, value=m_name)
        c2 = ws_analytics.cell(row=row_idx, column=2, value=m_val)
        c3 = ws_analytics.cell(row=row_idx, column=3, value=m_target)
        c4 = ws_analytics.cell(row=row_idx, column=4, value=m_stat)
        for c in [c1, c2, c3, c4]:
            c.border = thin_border
            if row_idx % 2 == 0:
                c.fill = zebra_fill
        c2.font = metric_val_font
        c2.alignment = Alignment(horizontal="center")
        c3.alignment = Alignment(horizontal="center")
        c4.alignment = Alignment(horizontal="center")

    # Auto-adjust column widths on all sheets
    for ws in [ws_apps, ws_matches, ws_analytics]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row in [1, 2]:
                    continue
                val = str(cell.value or "")
                if len(val) > max_len:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(output_path)
    return os.path.getsize(output_path)
