"""Gemini LLM Client Implementation"""

from typing import Iterator
import google.generativeai as genai


class GeminiClient:
    """Gemini API client implementation"""

    def __init__(self, api_key: str, model: str = "gemini-pro", temperature: float = 0.7):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._generation_config = genai.GenerationConfig(temperature=temperature)

    def generate(self, prompt: str) -> str:
        """Generate a complete response"""
        response = self._model.generate_content(prompt, generation_config=self._generation_config)
        return response.text

    def stream_generate(self, prompt: str) -> Iterator[str]:
        """Stream generate response"""
        response = self._model.generate_content(
            prompt, generation_config=self._generation_config, stream=True
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def modify_temperature(self, temperature: float) -> None:
        """Modify generation temperature"""
        self._generation_config = genai.GenerationConfig(temperature=temperature)
