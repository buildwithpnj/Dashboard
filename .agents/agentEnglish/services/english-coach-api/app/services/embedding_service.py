import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generates real vector embeddings via OpenAI API, falling back to mock stubs offline."""

    def __init__(self):
        self.client = None
        # Initialize active OpenAI AsyncClient if enabled in configs
        if settings.OPENAI_API_KEY and settings.MODEL_PROVIDER.lower() == "openai":
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                logger.warning("openai package not installed. Falling back to mock embeddings.")

    async def get_embedding(self, text: str) -> List[float]:
        """Generates 1536-dimension float vectors for the query string."""
        if not text or not text.strip():
            return [0.0] * 1536

        if self.client:
            try:
                logger.info(f"Generating OpenAI text embedding for input: '{text[:20]}...'")
                response = await self.client.embeddings.create(
                    input=[text],
                    model="text-embedding-3-small"
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Failed to generate OpenAI embedding: {e}. Falling back to mock.")
                
        # Default mock vector (1536 dimensions match text-embedding-3-small)
        return [0.01] * 1536
