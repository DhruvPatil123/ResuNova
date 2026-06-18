from fpdf import FPDF
from typing import List
from data.schema import ResumeData

class ATSResumePDF(FPDF):
    def header(self):
        pass # Custom header handled in build_pdf

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

class PDFGenerator:
    def __init__(self):
        self.pdf = ATSResumePDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def build_pdf(self, data: ResumeData) -> bytes:
        self.pdf.add_page()

        # --- HEADER ---
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, data.full_name, ln=True, align="C")

        self.pdf.set_font("Arial", "", 10)
        contact_info = f"{data.email} | {data.phone} | {data.linkedin} | {data.github}"
        self.pdf.cell(0, 10, contact_info, ln=True, align="C")
        self.pdf.ln(5)

        # --- SUMMARY ---
        if data.summary:
            self._add_section_title("PROFESSIONAL SUMMARY")
            self.pdf.set_font("Arial", "", 11)
            self.pdf.multi_cell(0, 6, data.summary)
            self.pdf.ln(5)

        # --- EXPERIENCE ---
        if data.experience:
            self._add_section_title("WORK EXPERIENCE")
            for exp in data.experience:
                self.pdf.set_font("Arial", "B", 11)
                self.pdf.cell(0, 6, f"{exp.role} at {exp.company}", ln=True)

                self.pdf.set_font("Arial", "I", 10)
                self.pdf.cell(0, 6, f"{exp.location} | {exp.start_date} - {exp.end_date}", ln=True)

                self.pdf.set_font("Arial", "", 11)
                for bullet in exp.description:
                    self.pdf.multi_cell(0, 6, f"• {bullet}")
                self.pdf.ln(3)

        # --- EDUCATION ---
        if data.education:
            self.pdf.ln(5)
            self._add_section_title("EDUCATION")
            for edu in data.education:
                self.pdf.set_font("Arial", "B", 11)
                self.pdf.cell(0, 6, f"{edu.institution}", ln=True)

                self.pdf.set_font("Arial", "", 11)
                self.pdf.cell(0, 6, f"{edu.degree} ({edu.start_date} - {edu.end_date})", ln=True)
                if edu.gpa:
                    self.pdf.cell(0, 6, f"GPA: {edu.gpa}", ln=True)
                self.pdf.ln(3)

        # --- SKILLS ---
        if data.skills:
            self.pdf.ln(5)
            self._add_section_title("SKILLS")
            self.pdf.set_font("Arial", "", 11)
            skills_text = ", ".join(data.skills)
            self.pdf.multi_cell(0, 6, skills_text)

        return self.pdf.output()

    def _add_section_title(self, title: str):
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.set_fill_color(230, 230, 230)
        self.pdf.cell(0, 8, title, ln=True, fill=True, align="C")
        self.pdf.ln(2)
