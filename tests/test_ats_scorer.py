import pytest
from core.ats_scorer import ATSScorer
from data.schema import ResumeData, Experience, Education


@pytest.fixture
def scorer():
    return ATSScorer()


@pytest.fixture
def full_resume():
    return ResumeData(
        full_name="Jane Doe",
        email="jane@example.com",
        summary="Experienced software engineer with 5 years in backend systems.",
        experience=[
            Experience(
                company="Acme Corp",
                role="Senior Engineer",
                description=[
                    "Increased API throughput by 40% via caching layer",
                    "Managed team of 8 engineers across 3 projects",
                    "Saved $200K annually by migrating to serverless",
                ],
            ),
        ],
        education=[Education(institution="MIT", degree="BS CS")],
        skills=["Python", "Go", "Kubernetes", "Docker", "AWS"],
    )


@pytest.fixture
def empty_resume():
    return ResumeData()


class TestATSScorerInit:
    def test_required_sections(self, scorer):
        assert scorer.required_sections == ["Experience", "Education", "Skills", "Summary"]


class TestStructuralScore:
    def test_all_sections_present(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "Python developer needed")
        assert result["breakdown"]["structure"] == 20

    def test_no_sections_present(self, scorer, empty_resume):
        result = scorer.analyze(empty_resume, "Python developer needed")
        assert result["breakdown"]["structure"] == 0

    def test_partial_sections(self, scorer):
        resume = ResumeData(summary="Some summary", skills=["Python"])
        result = scorer.analyze(resume, "Python developer needed")
        assert result["breakdown"]["structure"] == 10

    def test_missing_section_suggestion(self, scorer, empty_resume):
        result = scorer.analyze(empty_resume, "Python developer needed")
        assert any("missing" in s.lower() for s in result["suggestions"])


class TestKeywordMatching:
    def test_full_keyword_match(self, scorer):
        resume = ResumeData(
            summary="Python developer expert",
            experience=[
                Experience(
                    company="X",
                    role="Python Developer",
                    description=["Built python apps"],
                )
            ],
            education=[Education(institution="MIT", degree="CS")],
            skills=["Python", "Django", "REST"],
        )
        jd = "Python Python Python"
        result = scorer.analyze(resume, jd)
        assert result["breakdown"]["keywords"] == 40

    def test_no_keyword_match(self, scorer):
        resume = ResumeData(
            summary="Java developer",
            experience=[Experience(company="X", role="Java Dev", description=["Java"])],
            education=[Education(institution="MIT", degree="CS")],
            skills=["Java"],
        )
        jd = "Python Django FastAPI expert needed"
        result = scorer.analyze(resume, jd)
        assert result["breakdown"]["keywords"] < 40

    def test_empty_jd_gives_full_keyword_score(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "")
        assert result["breakdown"]["keywords"] == 40

    def test_empty_jd_suggestion(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "")
        assert any("job description" in s.lower() for s in result["suggestions"])

    def test_case_insensitive_matching(self, scorer):
        resume = ResumeData(
            summary="python developer",
            experience=[],
            education=[],
            skills=["PYTHON"],
        )
        jd = "Python"
        result = scorer.analyze(resume, jd)
        assert result["breakdown"]["keywords"] == 40

    def test_missing_keywords_suggestion(self, scorer):
        resume = ResumeData(
            summary="I do things",
            experience=[Experience(company="X", role="Dev", description=["stuff"])],
            education=[Education(institution="MIT", degree="CS")],
            skills=[],
        )
        jd = "Python Django FastAPI Kubernetes Docker AWS React Node"
        result = scorer.analyze(resume, jd)
        suggestions_text = " ".join(result["suggestions"]).lower()
        assert "integrate" in suggestions_text or "key skills" in suggestions_text


class TestMetricDensity:
    def test_all_bullets_have_metrics(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "Software engineer")
        assert result["breakdown"]["metrics"] == 40

    def test_no_bullets(self, scorer):
        resume = ResumeData(
            summary="Engineer",
            experience=[Experience(company="X", role="Dev", description=[])],
            education=[Education(institution="MIT", degree="CS")],
            skills=["Python"],
        )
        result = scorer.analyze(resume, "Developer needed")
        assert result["breakdown"]["metrics"] == 0
        assert any("work experience" in s.lower() or "impact" in s.lower() for s in result["suggestions"])

    def test_no_experience(self, scorer):
        resume = ResumeData(
            summary="Engineer",
            experience=[],
            education=[Education(institution="MIT", degree="CS")],
            skills=["Python"],
        )
        result = scorer.analyze(resume, "Developer needed")
        assert result["breakdown"]["metrics"] == 0

    def test_low_metric_density_suggestion(self, scorer):
        resume = ResumeData(
            summary="Developer",
            experience=[
                Experience(
                    company="X",
                    role="Dev",
                    description=[
                        "Wrote code for the backend",
                        "Worked on frontend components",
                        "Attended meetings",
                    ],
                )
            ],
            education=[Education(institution="MIT", degree="CS")],
            skills=["Python"],
        )
        result = scorer.analyze(resume, "Developer needed")
        assert any("quantify" in s.lower() for s in result["suggestions"])

    def test_metric_pattern_percentage(self, scorer):
        resume = ResumeData(
            summary="Dev",
            experience=[
                Experience(company="X", role="Dev", description=["Improved speed by 50%"])
            ],
            education=[],
            skills=[],
        )
        result = scorer.analyze(resume, "Dev")
        assert result["breakdown"]["metrics"] == 40

    def test_metric_pattern_dollar(self, scorer):
        resume = ResumeData(
            summary="Dev",
            experience=[
                Experience(company="X", role="Dev", description=["Saved $100K in costs"])
            ],
            education=[],
            skills=[],
        )
        result = scorer.analyze(resume, "Dev")
        assert result["breakdown"]["metrics"] == 40

    def test_metric_pattern_action_verbs(self, scorer):
        resume = ResumeData(
            summary="Dev",
            experience=[
                Experience(
                    company="X",
                    role="Dev",
                    description=["Led the team to success"],
                )
            ],
            education=[],
            skills=[],
        )
        result = scorer.analyze(resume, "Dev")
        assert result["breakdown"]["metrics"] == 40


class TestOverallScore:
    def test_perfect_score(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "Senior Engineer Python Go Kubernetes")
        assert result["score"] <= 100
        assert result["score"] > 0

    def test_score_is_rounded(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "Python developer")
        assert isinstance(result["score"], int)

    def test_result_has_required_keys(self, scorer, full_resume):
        result = scorer.analyze(full_resume, "Python")
        assert "score" in result
        assert "suggestions" in result
        assert "breakdown" in result
        assert "structure" in result["breakdown"]
        assert "keywords" in result["breakdown"]
        assert "metrics" in result["breakdown"]

    def test_zero_score_empty_resume_with_jd(self, scorer, empty_resume):
        result = scorer.analyze(empty_resume, "Python Django FastAPI")
        assert result["score"] < 50


class TestExtractKeywords:
    def test_filters_stop_words(self, scorer):
        keywords = scorer._extract_keywords("the and with this that from their will")
        assert "the" not in keywords
        assert "and" not in keywords

    def test_extracts_meaningful_words(self, scorer):
        keywords = scorer._extract_keywords("Python Django REST API development")
        assert "python" in keywords
        assert "django" in keywords

    def test_returns_top_10(self, scorer):
        long_text = " ".join([f"keyword{i}" for i in range(50)])
        keywords = scorer._extract_keywords(long_text)
        assert len(keywords) <= 10

    def test_empty_text(self, scorer):
        keywords = scorer._extract_keywords("")
        assert keywords == []

    def test_short_words_filtered(self, scorer):
        keywords = scorer._extract_keywords("go is at do me")
        assert len(keywords) == 0


class TestGetFullResumeText:
    def test_includes_summary(self, scorer, full_resume):
        text = scorer._get_full_resume_text(full_resume)
        assert "Experienced software engineer" in text

    def test_includes_skills(self, scorer, full_resume):
        text = scorer._get_full_resume_text(full_resume)
        assert "Python" in text

    def test_includes_experience(self, scorer, full_resume):
        text = scorer._get_full_resume_text(full_resume)
        assert "Acme Corp" in text
        assert "40%" in text

    def test_empty_resume(self, scorer, empty_resume):
        text = scorer._get_full_resume_text(empty_resume)
        assert isinstance(text, str)
