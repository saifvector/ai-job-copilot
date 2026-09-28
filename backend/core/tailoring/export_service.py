"""
Export Service for Phase 7 AI Resume Tailoring Engine.
Generates production-quality exports in PDF, DOCX, and Markdown formats.
"""
import io
from typing import Any, Dict, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
from schemas.tailoring import ResumeVersionDTO


class ResumeExportService:
    """
    Renders structured ResumeVersionDTO into Markdown, DOCX, or PDF binary streams.
    """

    @classmethod
    def export_markdown(
        cls,
        version: ResumeVersionDTO,
        candidate_name: str = "Candidate Name",
        contact_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generates standard Markdown formatted resume.
        """
        contact = contact_info or {}
        contact_parts = []
        if contact.get("email"):
            contact_parts.append(contact["email"])
        if contact.get("phone"):
            contact_parts.append(contact["phone"])
        if contact.get("location"):
            contact_parts.append(contact["location"])
        contact_line = " | ".join(contact_parts) if contact_parts else "Email: user@example.com"

        lines = [
            f"# {candidate_name}",
            f"*{contact_line}*",
            "",
            "---",
            "",
            "## PROFESSIONAL SUMMARY",
            version.summary.strip(),
            "",
        ]

        if version.skills:
            lines.append("## CORE COMPETENCIES & TECHNICAL SKILLS")
            for group in version.skills:
                skills_str = ", ".join(group.skills)
                lines.append(f"- **{group.category}**: {skills_str}")
            lines.append("")

        if version.experience:
            lines.append("## PROFESSIONAL EXPERIENCE")
            for exp in version.experience:
                date_str = f" ({exp.start_date} – {exp.end_date})" if (exp.start_date or exp.end_date) else ""
                lines.append(f"### {exp.role} — **{exp.company}**{date_str}")
                if exp.description:
                    lines.append(f"*{exp.description.strip()}*")
                for bullet in exp.bullet_points:
                    lines.append(f"- {bullet.strip()}")
                lines.append("")

        if version.projects:
            lines.append("## TECHNICAL PROJECTS")
            for proj in version.projects:
                tech_str = f" | *Tech: {', '.join(proj.technologies)}*" if proj.technologies else ""
                lines.append(f"### {proj.title}{tech_str}")
                lines.append(f"{proj.description.strip()}")
                for b in proj.bullet_points:
                    lines.append(f"- {b.strip()}")
                lines.append("")

        if version.education:
            lines.append("## EDUCATION & CREDENTIALS")
            for edu in version.education:
                field = f" in {edu.field_of_study}" if edu.field_of_study else ""
                date_str = f" ({edu.start_date} – {edu.end_date})" if (edu.start_date or edu.end_date) else ""
                lines.append(f"- **{edu.degree}{field}** — {edu.institution}{date_str}")
            lines.append("")

        if version.certifications:
            lines.append("## CERTIFICATIONS")
            for cert in version.certifications:
                date_str = f" ({cert.issue_date})" if cert.issue_date else ""
                lines.append(f"- **{cert.name}** — {cert.issuer}{date_str}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def export_docx(
        cls,
        version: ResumeVersionDTO,
        candidate_name: str = "Candidate Name",
        contact_info: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Generates standard formatted DOCX binary document using python-docx.
        """
        doc = docx.Document()

        # Set standard margins (0.5 inch for modern resumes)
        sections = doc.sections
        for s in sections:
            s.top_margin = Inches(0.5)
            s.bottom_margin = Inches(0.5)
            s.left_margin = Inches(0.6)
            s.right_margin = Inches(0.6)

        # Candidate Name Heading
        title_p = doc.add_paragraph()
        title_p.paragraph_format.space_after = Pt(2)
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_p.add_run(candidate_name)
        run.bold = True
        run.font.size = Pt(20)
        run.font.color.rgb = RGBColor(17, 24, 39)

        # Contact Subheading
        contact = contact_info or {}
        contact_parts = []
        if contact.get("email"):
            contact_parts.append(contact["email"])
        if contact.get("phone"):
            contact_parts.append(contact["phone"])
        if contact.get("location"):
            contact_parts.append(contact["location"])
        contact_str = " | ".join(contact_parts) if contact_parts else "Email: candidate@example.com"

        sub_p = doc.add_paragraph()
        sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_p.paragraph_format.space_after = Pt(12)
        sub_run = sub_p.add_run(contact_str)
        sub_run.font.size = Pt(9.5)
        sub_run.font.color.rgb = RGBColor(107, 114, 128)

        def add_section_header(text: str) -> None:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text.upper())
            r.bold = True
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(31, 41, 55)

        # Summary Section
        add_section_header("Professional Summary")
        sum_p = doc.add_paragraph()
        sum_p.paragraph_format.space_after = Pt(8)
        sum_run = sum_p.add_run(version.summary.strip())
        sum_run.font.size = Pt(10)

        # Skills Section
        if version.skills:
            add_section_header("Core Competencies & Skills")
            for group in version.skills:
                sp = doc.add_paragraph()
                sp.paragraph_format.space_after = Pt(2)
                cat_run = sp.add_run(f"• {group.category}: ")
                cat_run.bold = True
                cat_run.font.size = Pt(9.5)
                val_run = sp.add_run(", ".join(group.skills))
                val_run.font.size = Pt(9.5)

        # Experience Section
        if version.experience:
            add_section_header("Professional Experience")
            for exp in version.experience:
                ep = doc.add_paragraph()
                ep.paragraph_format.space_before = Pt(4)
                ep.paragraph_format.space_after = Pt(2)
                role_run = ep.add_run(f"{exp.role} — ")
                role_run.bold = True
                role_run.font.size = Pt(10)
                comp_run = ep.add_run(exp.company)
                comp_run.bold = True
                comp_run.font.size = Pt(10)

                date_str = f" | {exp.start_date} – {exp.end_date}" if (exp.start_date or exp.end_date) else ""
                if date_str:
                    date_run = ep.add_run(date_str)
                    date_run.italic = True
                    date_run.font.size = Pt(9)
                    date_run.font.color.rgb = RGBColor(107, 114, 128)

                for bullet in exp.bullet_points:
                    bp = doc.add_paragraph(style="List Bullet")
                    bp.paragraph_format.space_after = Pt(1.5)
                    bp.paragraph_format.space_before = Pt(0)
                    brun = bp.add_run(bullet.strip())
                    brun.font.size = Pt(9.5)

        # Projects Section
        if version.projects:
            add_section_header("Technical Projects")
            for proj in version.projects:
                pp = doc.add_paragraph()
                pp.paragraph_format.space_before = Pt(3)
                pp.paragraph_format.space_after = Pt(1)
                prun = pp.add_run(proj.title)
                prun.bold = True
                prun.font.size = Pt(10)
                if proj.technologies:
                    trun = pp.add_run(f" ({', '.join(proj.technologies)})")
                    trun.font.size = Pt(9)
                    trun.italic = True
                    trun.font.color.rgb = RGBColor(107, 114, 128)

                if proj.description:
                    dp = doc.add_paragraph()
                    dp.paragraph_format.space_after = Pt(1.5)
                    drun = dp.add_run(proj.description.strip())
                    drun.font.size = Pt(9.5)

                for bullet in proj.bullet_points:
                    bp = doc.add_paragraph(style="List Bullet")
                    bp.paragraph_format.space_after = Pt(1.5)
                    brun = bp.add_run(bullet.strip())
                    brun.font.size = Pt(9.5)

        # Education Section
        if version.education:
            add_section_header("Education")
            for edu in version.education:
                edp = doc.add_paragraph()
                edp.paragraph_format.space_after = Pt(2)
                deg_run = edp.add_run(edu.degree)
                deg_run.bold = True
                deg_run.font.size = Pt(10)
                field_str = f" in {edu.field_of_study}" if edu.field_of_study else ""
                deg_run2 = edp.add_run(f"{field_str} — {edu.institution}")
                deg_run2.font.size = Pt(10)
                date_str = f" ({edu.start_date} – {edu.end_date})" if (edu.start_date or edu.end_date) else ""
                if date_str:
                    drun = edp.add_run(date_str)
                    drun.italic = True
                    drun.font.size = Pt(9)
                    drun.font.color.rgb = RGBColor(107, 114, 128)

        # Certifications Section
        if version.certifications:
            add_section_header("Certifications")
            for cert in version.certifications:
                cp = doc.add_paragraph()
                cp.paragraph_format.space_after = Pt(2)
                crun = cp.add_run(f"• {cert.name}")
                crun.bold = True
                crun.font.size = Pt(9.5)
                crun2 = cp.add_run(f" — {cert.issuer}")
                crun2.font.size = Pt(9.5)
                if cert.issue_date:
                    drun = cp.add_run(f" ({cert.issue_date})")
                    drun.font.size = Pt(9)
                    drun.font.color.rgb = RGBColor(107, 114, 128)

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def export_pdf(
        cls,
        version: ResumeVersionDTO,
        candidate_name: str = "Candidate Name",
        contact_info: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Generates standard ATS-parseable PDF document using ReportLab.
        """
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            leftMargin=36,  # 0.5 inch
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        name_style = ParagraphStyle(
            "CandidateName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=1,  # Center
            textColor=colors.HexColor("#111827"),
        )
        contact_style = ParagraphStyle(
            "ContactInfo",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=1,  # Center
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=8,
        )
        section_heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1F2937"),
            spaceBefore=6,
            spaceAfter=2,
            textTransform="uppercase",
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#374151"),
            spaceAfter=4,
        )
        bold_item_style = ParagraphStyle(
            "BoldItem",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#111827"),
        )
        bullet_style = ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            leftIndent=14,
            firstLineIndent=-10,
            textColor=colors.HexColor("#374151"),
            spaceAfter=2,
        )

        elements = []

        # Header: Name and Contact
        elements.append(Paragraph(candidate_name, name_style))
        contact = contact_info or {}
        contact_parts = []
        if contact.get("email"):
            contact_parts.append(contact["email"])
        if contact.get("phone"):
            contact_parts.append(contact["phone"])
        if contact.get("location"):
            contact_parts.append(contact["location"])
        contact_str = " &nbsp;|&nbsp; ".join(contact_parts) if contact_parts else "Email: candidate@example.com"
        elements.append(Paragraph(contact_str, contact_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB"), spaceAfter=6))

        def add_header(title: str) -> None:
            elements.append(Paragraph(title, section_heading_style))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceAfter=4))

        # Professional Summary
        add_header("PROFESSIONAL SUMMARY")
        elements.append(Paragraph(version.summary.strip(), body_style))
        elements.append(Spacer(1, 4))

        # Core Skills
        if version.skills:
            add_header("CORE COMPETENCIES & TECHNICAL SKILLS")
            for group in version.skills:
                line = f"<b>{group.category}:</b> {', '.join(group.skills)}"
                elements.append(Paragraph(line, body_style))
            elements.append(Spacer(1, 4))

        # Experience
        if version.experience:
            add_header("PROFESSIONAL EXPERIENCE")
            for exp in version.experience:
                date_str = f"&nbsp;&nbsp;<i>({exp.start_date} – {exp.end_date})</i>" if (exp.start_date or exp.end_date) else ""
                item_header = f"<b>{exp.role}</b> — {exp.company}{date_str}"
                elements.append(Paragraph(item_header, bold_item_style))
                for bullet in exp.bullet_points:
                    elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                elements.append(Spacer(1, 3))
            elements.append(Spacer(1, 2))

        # Projects
        if version.projects:
            add_header("TECHNICAL PROJECTS")
            for proj in version.projects:
                tech_str = f"&nbsp;&nbsp;<i>({', '.join(proj.technologies)})</i>" if proj.technologies else ""
                elements.append(Paragraph(f"<b>{proj.title}</b>{tech_str}", bold_item_style))
                if proj.description:
                    elements.append(Paragraph(proj.description.strip(), body_style))
                for bullet in proj.bullet_points:
                    elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                elements.append(Spacer(1, 3))

        # Education
        if version.education:
            add_header("EDUCATION & CREDENTIALS")
            for edu in version.education:
                field = f" in {edu.field_of_study}" if edu.field_of_study else ""
                date_str = f"&nbsp;&nbsp;<i>({edu.start_date} – {edu.end_date})</i>" if (edu.start_date or edu.end_date) else ""
                line = f"<b>{edu.degree}{field}</b> — {edu.institution}{date_str}"
                elements.append(Paragraph(line, body_style))
            elements.append(Spacer(1, 3))

        # Certifications
        if version.certifications:
            add_header("CERTIFICATIONS")
            for cert in version.certifications:
                date_str = f"&nbsp;&nbsp;<i>({cert.issue_date})</i>" if cert.issue_date else ""
                line = f"<b>{cert.name}</b> — {cert.issuer}{date_str}"
                elements.append(Paragraph(line, body_style))
            elements.append(Spacer(1, 3))

        doc.build(elements)
        buf.seek(0)
        return buf.getvalue()
