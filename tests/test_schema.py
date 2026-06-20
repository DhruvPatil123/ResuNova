import pytest
from data.schema import ResumeData, Experience, Education, Project


class TestExperience:
    def test_defaults(self):
        exp = Experience()
        assert exp.company == ""
        assert exp.role == ""
        assert exp.location == ""
        assert exp.start_date == ""
        assert exp.end_date == ""
        assert exp.description == []

    def test_with_values(self):
        exp = Experience(
            company="Acme Corp",
            role="Engineer",
            location="NYC",
            start_date="2020-01",
            end_date="2023-06",
            description=["Led team of 5", "Built API"],
        )
        assert exp.company == "Acme Corp"
        assert exp.role == "Engineer"
        assert exp.description == ["Led team of 5", "Built API"]

    def test_description_is_independent_list(self):
        exp1 = Experience()
        exp2 = Experience()
        exp1.description.append("bullet")
        assert exp2.description == []

    def test_serialization_round_trip(self):
        exp = Experience(company="X", role="Y", description=["a", "b"])
        data = exp.model_dump()
        restored = Experience(**data)
        assert restored == exp


class TestEducation:
    def test_defaults(self):
        edu = Education()
        assert edu.institution == ""
        assert edu.degree == ""
        assert edu.gpa is None

    def test_with_gpa(self):
        edu = Education(institution="MIT", degree="BS CS", gpa="3.9")
        assert edu.gpa == "3.9"

    def test_without_gpa(self):
        edu = Education(institution="MIT", degree="BS CS")
        assert edu.gpa is None

    def test_serialization_round_trip(self):
        edu = Education(institution="MIT", degree="BS", gpa="4.0")
        data = edu.model_dump()
        restored = Education(**data)
        assert restored == edu


class TestProject:
    def test_defaults(self):
        proj = Project()
        assert proj.name == ""
        assert proj.link == ""
        assert proj.description == []
        assert proj.tech_stack == []

    def test_with_values(self):
        proj = Project(
            name="ChatBot",
            link="https://github.com/x/y",
            description=["Real-time NLP chatbot"],
            tech_stack=["Python", "FastAPI"],
        )
        assert proj.name == "ChatBot"
        assert len(proj.tech_stack) == 2


class TestResumeData:
    def test_defaults(self):
        rd = ResumeData()
        assert rd.full_name == ""
        assert rd.email == ""
        assert rd.phone == ""
        assert rd.linkedin == ""
        assert rd.github == ""
        assert rd.portfolio == ""
        assert rd.summary == ""
        assert rd.experience == []
        assert rd.education == []
        assert rd.skills == []
        assert rd.projects == []
        assert rd.certifications == []

    def test_with_nested_models(self):
        rd = ResumeData(
            full_name="Jane Doe",
            email="jane@example.com",
            skills=["Python", "Go"],
            experience=[
                Experience(company="Acme", role="SWE", description=["Did stuff"]),
            ],
            education=[
                Education(institution="MIT", degree="BS CS"),
            ],
        )
        assert rd.full_name == "Jane Doe"
        assert len(rd.experience) == 1
        assert rd.experience[0].company == "Acme"
        assert len(rd.education) == 1

    def test_full_serialization_round_trip(self):
        rd = ResumeData(
            full_name="John",
            email="john@test.com",
            skills=["Rust"],
            experience=[Experience(company="X", role="Y")],
            education=[Education(institution="Z", degree="W")],
            projects=[Project(name="P", tech_stack=["TS"])],
            certifications=["AWS"],
        )
        data = rd.model_dump()
        restored = ResumeData(**data)
        assert restored == rd

    def test_from_dict_with_nested_dicts(self):
        raw = {
            "full_name": "Test",
            "experience": [{"company": "C", "role": "R", "description": ["b1"]}],
            "education": [{"institution": "I", "degree": "D"}],
        }
        rd = ResumeData(**raw)
        assert rd.experience[0].company == "C"
        assert rd.education[0].institution == "I"

    def test_empty_skills_list(self):
        rd = ResumeData(skills=[])
        assert rd.skills == []

    def test_multiple_certifications(self):
        rd = ResumeData(certifications=["AWS", "GCP", "Azure"])
        assert len(rd.certifications) == 3
