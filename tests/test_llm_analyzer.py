"""Tests for app.services.llm_analyzer (Ollama only)."""
import unittest
from unittest.mock import patch, MagicMock


class TestFactChecker(unittest.TestCase):
    """Test FactChecker with mocked Ollama API."""

    def test_init_succeeds(self):
        from app.services.llm_analyzer import FactChecker
        checker = FactChecker()
        self.assertIsNotNone(checker)

    @patch("app.services.llm_analyzer.requests.post")
    def test_analyze_claims_returns_markdown_from_ollama(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"response": "## Analysis\n\nTruth Score: 7/10"},
            raise_for_status=MagicMock(),
        )
        from app.services.llm_analyzer import FactChecker
        checker = FactChecker()
        financial_data = {
            "Ticker": "AAPL",
            "Company Name": "Apple Inc",
            "Total Revenue": "$100B",
            "Net Income": "$20B",
        }
        result = checker.analyze_claims(financial_data, "We had record revenue.")
        self.assertIn("Truth Score", result)
        self.assertIn("7", result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "http://localhost:11434/api/generate")
        self.assertIn("prompt", call_args[1]["json"])

    @patch("app.services.llm_analyzer.requests.post")
    def test_analyze_claims_returns_error_when_ollama_connection_fails(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        from app.services.llm_analyzer import FactChecker
        checker = FactChecker()
        result = checker.analyze_claims({"Ticker": "X", "Company Name": "Y"}, "Some text")
        self.assertIsInstance(result, str)
        self.assertIn("Ollama", result)
        self.assertIn("running", result.lower())


if __name__ == "__main__":
    unittest.main()
