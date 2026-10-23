"""Tests for app.config (Ollama-only)."""
import unittest
from unittest.mock import patch


class TestConfig(unittest.TestCase):
    """Test configuration."""

    def test_get_ollama_model_default(self):
        with patch("app.config.os.getenv", return_value=None):
            from app.config import get_ollama_model
            self.assertEqual(get_ollama_model(), "llama3.2")

    def test_get_ollama_model_from_env(self):
        with patch("app.config.os.getenv", side_effect=lambda k, d=None: "mistral" if k == "OLLAMA_MODEL" else d):
            from app.config import get_ollama_model
            self.assertEqual(get_ollama_model(), "mistral")

    def test_validate_config_always_true(self):
        from app.config import validate_config
        self.assertTrue(validate_config())

    def test_get_llm_display_name_returns_ollama(self):
        from app.config import get_llm_display_name
        self.assertEqual(get_llm_display_name(), "Ollama")
