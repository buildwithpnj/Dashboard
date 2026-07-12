from app.providers.base import BaseLLMProvider, ProviderResponse

class GeminiLLMProvider(BaseLLMProvider):
    """Gemini API provider stub raising NotImplementedError for the V0 release."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_structured_response(self, prompt: str, system_prompt: str) -> ProviderResponse:
        raise NotImplementedError("Gemini provider is not implemented/configured for V0.")
