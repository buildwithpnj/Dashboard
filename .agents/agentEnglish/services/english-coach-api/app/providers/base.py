import abc
from dataclasses import dataclass

@dataclass
class ProviderResponse:
    """Standardized response from any LLM provider containing content and usage statistics."""
    raw_content: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    estimated_cost_usd: float
    latency_ms: float

class BaseLLMProvider(abc.ABC):
    """Abstract interface defining the requirements for an LLM text generator."""

    @abc.abstractmethod
    async def generate_structured_response(self, prompt: str, system_prompt: str) -> ProviderResponse:
        """Generates text from the provider model given the prompt and system_prompt.
        
        Args:
            prompt: The user input text.
            system_prompt: System instructions / constraints.

        Returns:
            The structured ProviderResponse object.
        """
        pass
