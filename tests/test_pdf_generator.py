import pytest
from core.pdf_generator import PDFGenerator, ATSResumePDF
from data.schema import ResumeData, Experience, Education


@pytest.fixture
def generator():
    return PDFGenerator()


@pytest.fixture
def full_resume():
    return ResumeData(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="555-1234",
        linkedin="linkedin.com/in/jane",
        github="github.com/jane",
        summary="Experienced software engineer with 5 years building scalable systems.",
        experience=[
            Experience(
                company="Acme Corp",
                role="Senior Engineer",
                location="San Francisco, CA",
                start_date="2020-01",
                end_date="2023-06",
                description=[
                    "Increased API throughput by 40%",
                    "Led team of 8 engineers",
                ],
            ),
        ],
        education=[
            Education(
                institution="MIT",
                degree="BS Computer Science",
                start_date="2016",
                end_date="2020",
                gpa="3.9",
            ),
        ],
        skills=["Python", "Go", "Kubernetes", "Docker"],
    )


def _is_pdf(data) -> bool:
    return bytes(data)[:5] == b"%PDF-"


class TestATSResumePDF:
    def test_is_fpdf_subclass(self):
        from fpdf import FPDF
        assert issubclass(ATSResumePDF, FPDF)

    def test_footer_sets_page_number(self):
        pdf = ATSResumePDF()
        pdf.add_page()
        pdf.footer()
        output = pdf.output()
        assert len(output) > 0
        assert _is_pdf(output)


class TestPDFGenerator:
    def test_build_pdf_returns_pdf(self, generator, full_resume):
        result = generator.build_pdf(full_resume)
        assert _is_pdf(result)

    def test_build_pdf_nonempty(self, generator, full_resume):
        result = generator.build_pdf(full_resume)
        assert len(result) > 100

    def test_build_pdf_minimal_resume(self):
        gen = PDFGenerator()
        resume = ResumeData(full_name="Test User")
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_empty_resume(self):
        gen = PDFGenerator()
        resume = ResumeData()
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_with_experience_only(self):
        gen = PDFGenerator()
        resume = ResumeData(
            full_name="Test",
            experience=[
                Experience(
                    company="X",
                    role="Dev",
                    location="NY",
                    start_date="2020",
                    end_date="2023",
                    description=["Built stuff"],
                )
            ],
        )
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_with_education_no_gpa(self):
        gen = PDFGenerator()
        resume = ResumeData(
            full_name="Test",
            education=[
                Education(institution="MIT", degree="BS CS", start_date="2016", end_date="2020"),
            ],
        )
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_with_education_with_gpa(self):
        gen = PDFGenerator()
        resume = ResumeData(
            full_name="Test",
            education=[
                Education(
                    institution="MIT",
                    degree="BS CS",
                    start_date="2016",
                    end_date="2020",
                    gpa="4.0",
                ),
            ],
        )
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_with_skills_only(self):
        gen = PDFGenerator()
        resume = ResumeData(full_name="Test", skills=["Python", "Rust", "Go"])
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_with_summary_only(self):
        gen = PDFGenerator()
        resume = ResumeData(full_name="Test", summary="A great engineer.")
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_multiple_experiences(self):
        gen = PDFGenerator()
        resume = ResumeData(
            full_name="Test",
            experience=[
                Experience(company="A", role="Dev1", description=["Task 1"]),
                Experience(company="B", role="Dev2", description=["Task 2", "Task 3"]),
            ],
        )
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_build_pdf_multiple_educations(self):
        gen = PDFGenerator()
        resume = ResumeData(
            full_name="Test",
            education=[
                Education(institution="MIT", degree="BS"),
                Education(institution="Stanford", degree="MS", gpa="3.8"),
            ],
        )
        result = gen.build_pdf(resume)
        assert _is_pdf(result)

    def test_section_title_method(self):
        gen = PDFGenerator()
        gen.pdf.add_page()
        gen._add_section_title("TEST SECTION")
        output = gen.pdf.output()
        assert _is_pdf(output)

    def test_new_generator_per_call(self):
        resume = ResumeData(full_name="User1")
        gen1 = PDFGenerator()
        pdf1 = gen1.build_pdf(resume)
        gen2 = PDFGenerator()
        pdf2 = gen2.build_pdf(resume)
        assert _is_pdf(pdf1)
        assert _is_pdf(pdf2)

    def test_full_resume_pdf_size(self, generator, full_resume):
        result = generator.build_pdf(full_resume)
        assert len(result) > 500
