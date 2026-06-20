import json
import pytest
from unittest.mock import patch, MagicMock
from core.ai_engine import AIEngine
from data.schema import Experience


class TestAIEngineInit:
    @patch("core.ai_engine.st")
    def test_init_no_key(self, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        assert engine.client is None

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_init_with_passed_key(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        engine = AIEngine(api_key="test-key-123")
        assert engine.api_key == "test-key-123"
        assert engine.client is not None
        mock_openai_cls.assert_called_once_with(api_key="test-key-123")

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_init_with_env_key(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"}):
            engine = AIEngine()
        assert engine.api_key == "env-key"
        mock_openai_cls.assert_called_once_with(api_key="env-key")

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_init_with_streamlit_secret(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = "st-key"
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        assert engine.api_key == "st-key"

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_passed_key_takes_priority(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = "st-key"
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"}):
            engine = AIEngine(api_key="passed-key")
        assert engine.api_key == "passed-key"


class TestIsReady:
    @patch("core.ai_engine.st")
    def test_not_ready_without_key(self, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        assert engine.is_ready() is False

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_ready_with_key(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        engine = AIEngine(api_key="key")
        assert engine.is_ready() is True


class TestGenerateResponse:
    @patch("core.ai_engine.st")
    def test_returns_warning_without_api_key(self, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        result = engine._generate_response("test prompt")
        assert "API Key missing" in result

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_successful_response(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "  Improved bullet point  "
        mock_client.chat.completions.create.return_value = mock_response

        engine = AIEngine(api_key="test-key")
        result = engine._generate_response("test prompt")
        assert result == "Improved bullet point"

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_api_error_handling(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

        engine = AIEngine(api_key="test-key")
        result = engine._generate_response("test prompt")
        assert "Error:" in result
        assert "Rate limit exceeded" in result


class TestQuantifyBullet:
    @patch("core.ai_engine.st")
    def test_without_api_key_returns_warning(self, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        result = engine.quantify_bullet("Worked on the backend")
        assert "API Key missing" in result

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_calls_generate_response(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Spearheaded backend optimization, reducing latency by 35%"
        mock_client.chat.completions.create.return_value = mock_response

        engine = AIEngine(api_key="test-key")
        result = engine.quantify_bullet("Worked on the backend")
        assert isinstance(result, str)
        assert len(result) > 0


class TestPolishWording:
    @patch("core.ai_engine.st")
    def test_without_api_key(self, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        result = engine.polish_wording("Some text")
        assert "API Key missing" in result

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_with_custom_tone(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Polished text"
        mock_client.chat.completions.create.return_value = mock_response

        engine = AIEngine(api_key="test-key")
        result = engine.polish_wording("text", tone="Professional")
        assert result == "Polished text"
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        assert "Professional" in prompt


class TestRewriteExperienceForJd:
    @patch("core.ai_engine.st")
    def test_not_ready_returns_original(self, mock_st):
        mock_st.secrets.get.return_value = None
        with patch.dict("os.environ", {}, clear=True):
            engine = AIEngine()
        exp_list = [Experience(company="Acme", role="Dev", description=["Did things"])]
        result = engine.rewrite_experience_for_jd(exp_list, "Python developer needed")
        assert result is exp_list

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_valid_json_response(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        rewritten = [
            {"role": "Dev", "company": "Acme", "location": "NY",
             "start_date": "2020", "end_date": "2023",
             "description": ["Engineered Python microservices"]},
        ]
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(rewritten)
        mock_client.chat.completions.create.return_value = mock_response

        engine = AIEngine(api_key="test-key")
        exp_list = [Experience(company="Acme", role="Dev", description=["Did things"])]
        result = engine.rewrite_experience_for_jd(exp_list, "Python developer needed")
        assert isinstance(result, list)
        assert result[0]["description"] == ["Engineered Python microservices"]

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_json_with_markdown_markers(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        rewritten = [{"role": "Dev", "company": "X", "description": ["Built APIs"]}]
        raw = "```json\n" + json.dumps(rewritten) + "\n```"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = raw
        mock_client.chat.completions.create.return_value = mock_response

        engine = AIEngine(api_key="test-key")
        exp_list = [Experience(company="X", role="Dev", description=["stuff"])]
        result = engine.rewrite_experience_for_jd(exp_list, "JD text")
        assert isinstance(result, list)
        assert result[0]["company"] == "X"

    @patch("core.ai_engine.st")
    @patch("core.ai_engine.OpenAI")
    def test_invalid_json_returns_original(self, mock_openai_cls, mock_st):
        mock_st.secrets.get.return_value = None
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not valid json at all {{"
        mock_client.chat.completions.create.return_value = mock_response

        engine = AIEngine(api_key="test-key")
        exp_list = [Experience(company="Acme", role="Dev", description=["Did things"])]
        result = engine.rewrite_experience_for_jd(exp_list, "JD text")
        assert result is exp_list
