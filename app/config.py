"""
Configuration module. LLM: Ollama only (local, no API key).
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_ollama_model() -> str:
    """Ollama model name (e.g. llama3.2, mistral). Default: llama3.2"""
    raw = os.getenv("OLLAMA_MODEL") or "llama3.2"
    return (raw.strip() or "llama3.2")


def validate_config() -> bool:
    """Always True; analysis uses Ollama (no key required)."""
    return True


def get_llm_display_name() -> str:
    """Human-readable name of the LLM backend."""
    return "Ollama"
