import io
import json
import pytest
from unittest.mock import patch, MagicMock
from core.parser import ResumeParser
from data.schema import ResumeData


class TestParseJson:
    def test_valid_json_minimal(self):
        data = json.dumps({"full_name": "Alice", "email": "alice@x.com"})
        result = ResumeParser.parse_json(data)
        assert isinstance(result, ResumeData)
        assert result.full_name == "Alice"
        assert result.email == "alice@x.com"

    def test_valid_json_with_nested(self):
        data = json.dumps({
            "full_name": "Bob",
            "experience": [{"company": "Acme", "role": "Dev", "description": ["Did things"]}],
            "education": [{"institution": "MIT", "degree": "BS"}],
            "skills": ["Python", "Go"],
        })
        result = ResumeParser.parse_json(data)
        assert result.full_name == "Bob"
        assert len(result.experience) == 1
        assert result.experience[0].company == "Acme"
        assert len(result.education) == 1

    def test_empty_json_object(self):
        result = ResumeParser.parse_json("{}")
        assert isinstance(result, ResumeData)
        assert result.full_name == ""

    def test_invalid_json_returns_default(self):
        result = ResumeParser.parse_json("not valid json{{{")
        assert isinstance(result, ResumeData)
        assert result.full_name == ""

    def test_json_with_extra_fields_ignored(self):
        data = json.dumps({"full_name": "Test", "unknown_field": "value"})
        result = ResumeParser.parse_json(data)
        assert result.full_name == "Test"

    def test_json_with_all_fields(self):
        data = json.dumps({
            "full_name": "Complete User",
            "email": "user@test.com",
            "phone": "123-456-7890",
            "linkedin": "https://linkedin.com/in/user",
            "github": "https://github.com/user",
            "portfolio": "https://user.dev",
            "summary": "Full stack developer",
            "skills": ["React", "Node"],
            "certifications": ["AWS SAA"],
        })
        result = ResumeParser.parse_json(data)
        assert result.full_name == "Complete User"
        assert result.phone == "123-456-7890"
        assert len(result.certifications) == 1


class TestParsePdf:
    def test_parse_pdf_returns_dict(self):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\nExperienced developer"
        mock_reader.pages = [mock_page]

        with patch("core.parser.PyPDF2.PdfReader", return_value=mock_reader):
            result = ResumeParser.parse_pdf(io.BytesIO(b"fake pdf"))

        assert isinstance(result, dict)
        assert "full_name" in result
        assert "summary" in result
        assert "raw_text" in result

    def test_parse_pdf_summary_truncation(self):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "A" * 1000
        mock_reader.pages = [mock_page]

        with patch("core.parser.PyPDF2.PdfReader", return_value=mock_reader):
            result = ResumeParser.parse_pdf(io.BytesIO(b"fake"))

        assert result["summary"].endswith("...")
        assert len(result["summary"]) == 503  # 500 chars + "..."

    def test_parse_pdf_multiple_pages(self):
        mock_reader = MagicMock()
        page1 = MagicMock()
        page1.extract_text.return_value = "Page 1 content"
        page2 = MagicMock()
        page2.extract_text.return_value = "Page 2 content"
        mock_reader.pages = [page1, page2]

        with patch("core.parser.PyPDF2.PdfReader", return_value=mock_reader):
            result = ResumeParser.parse_pdf(io.BytesIO(b"fake"))

        assert "Page 1 content" in result["raw_text"]
        assert "Page 2 content" in result["raw_text"]

    def test_parse_pdf_raw_text_preserved(self):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Full text here"
        mock_reader.pages = [mock_page]

        with patch("core.parser.PyPDF2.PdfReader", return_value=mock_reader):
            result = ResumeParser.parse_pdf(io.BytesIO(b"fake"))

        assert "Full text here" in result["raw_text"]

    def test_parse_pdf_placeholder_name(self):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Some content"
        mock_reader.pages = [mock_page]

        with patch("core.parser.PyPDF2.PdfReader", return_value=mock_reader):
            result = ResumeParser.parse_pdf(io.BytesIO(b"fake"))

        assert result["full_name"] == "Extracted Name"
