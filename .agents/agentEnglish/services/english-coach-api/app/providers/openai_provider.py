import asyncio
import logging
import time
from typing import Dict, Any, Optional
from app.providers.base import BaseLLMProvider, ProviderResponse

logger = logging.getLogger(__name__)

class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI API provider implementation with structured JSON outputs, timeouts, and retries."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o-mini",
        timeout: float = 15.0,
        max_retries: int = 1,
        max_completion_tokens: int = 180
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_completion_tokens = max_completion_tokens
        
        # Lazy import of openai
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)

    def _calculate_cost(self, input_tokens: int, output_tokens: int, cached_tokens: int) -> float:
        """Estimates token charges in USD for OpenAI engines (defaulting to gpt-4o-mini rates)."""
        # gpt-4o-mini pricing (per token):
        # Input (uncached): $0.150 / 1M = $0.00000015
        # Input (cached): $0.075 / 1M = $0.000000075
        # Output: $0.600 / 1M = $0.00000060
        
        is_mini = "mini" in self.model_name.lower()
        
        if is_mini:
            uncached_input = input_tokens - cached_tokens
            cost = (uncached_input * 0.00000015) + (cached_tokens * 0.000000075) + (output_tokens * 0.00000060)
            return cost
        else:
            # Fallback for gpt-4o:
            # Input (uncached): $2.50 / 1M = $0.0000025
            # Input (cached): $1.25 / 1M = $0.00000125
            # Output: $10.00 / 1M = $0.00001
            uncached_input = input_tokens - cached_tokens
            cost = (uncached_input * 0.0000025) + (cached_tokens * 0.00000125) + (output_tokens * 0.00001)
            return cost

    async def generate_structured_response(self, prompt: str, system_prompt: str) -> ProviderResponse:
        logger.info(f"OpenAI calling chat completion model={self.model_name}")
        
        # Retry loop logic
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                backoff_delay = 2.0 ** attempt
                logger.info(f"Retrying OpenAI call (attempt {attempt}/{self.max_retries}) after {backoff_delay}s...")
                await asyncio.sleep(backoff_delay)
                
            start_time = time.perf_counter()
            try:
                # Wrap call in asyncio.wait_for for strict timeout enforcing
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                        max_completion_tokens=self.max_completion_tokens,
                        temperature=0.1
                    ),
                    timeout=self.timeout
                )
                
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                
                # Extract token consumption details safely
                usage = response.usage
                input_tokens = getattr(usage, "prompt_tokens", 0)
                output_tokens = getattr(usage, "completion_tokens", 0)
                
                cached_tokens = 0
                if usage and hasattr(usage, "prompt_tokens_details"):
                    cached_tokens = getattr(usage.prompt_tokens_details, "cached_tokens", 0) or 0
                
                cost = self._calculate_cost(input_tokens, output_tokens, cached_tokens)
                raw_content = response.choices[0].message.content or "{}"
                
                return ProviderResponse(
                    raw_content=raw_content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cached_tokens=cached_tokens,
                    estimated_cost_usd=cost,
                    latency_ms=latency_ms
                )
                
            except asyncio.TimeoutError as t_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning(f"OpenAI call timed out after {latency_ms:.1f}ms on attempt {attempt}")
                last_exception = RuntimeError(f"OpenAI API call timed out after {self.timeout} seconds.")
            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning(f"OpenAI call failed after {latency_ms:.1f}ms on attempt {attempt}: {e}")
                last_exception = e
                
        raise last_exception or RuntimeError("Failed to generate OpenAI response.")
