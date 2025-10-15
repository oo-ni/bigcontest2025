"""Configuration Management"""

import os
from typing import Optional


class Config:
    """Application configuration from environment variables"""

    def __init__(self):
        self._api_key: Optional[str] = None
        self._model_name: str = "gemini-2.5-flash"
        self._temperature: float = 0.7

    def get_api_key(self) -> str:
        """Get Gemini API key from environment"""
        if self._api_key is None:
            key = os.getenv("GEMINI_API_KEY", "")
            if not key or key == "your_gemini_api_key_here":
                raise ValueError("GEMINI_API_KEY not configured")
            self._api_key = key
        return self._api_key

    def get_model_name(self) -> str:
        """Get model name"""
        return self._model_name

    def get_temperature(self) -> float:
        """Get temperature setting"""
        return self._temperature

    def modify_temperature(self, temperature: float) -> None:
        """Modify temperature setting"""
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        self._temperature = temperature
