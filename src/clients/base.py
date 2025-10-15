"""Base LLM Client Interface"""

from typing import Protocol, Iterator


class LLMClient(Protocol):
    """Protocol for LLM client implementations"""

    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM"""
        ...

    def stream_generate(self, prompt: str) -> Iterator[str]:
        """Stream generate response from the LLM"""
        ...
