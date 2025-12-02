"""
Configuration module for loading environment variables.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_gemini_api_key() -> Optional[str]:
    """
    Retrieve the Gemini API key from environment variables.
    
    Returns:
        Optional[str]: The API key if found, None otherwise
    """
    return os.getenv("GEMINI_API_KEY")


def validate_config() -> bool:
    """
    Validate that all required configuration is present.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    api_key = get_gemini_api_key()
    if not api_key or api_key == "your_key_here":
        return False
    return True

