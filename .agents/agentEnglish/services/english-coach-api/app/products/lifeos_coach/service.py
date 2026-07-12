import logging
import uuid
import time
from typing import Tuple, Dict, Any, Optional

from app.core.config import settings
from app.providers.base import BaseLLMProvider, ProviderResponse
from app.services.response_formatter import ResponseFormatter
from app.services.memory_service import MemoryService
from app.services.context_budget import enforce_context_budget
from app.core.log_config import log_structured_event

# Product-specific imports
from app.products.lifeos_coach.prompt_config import build_prompt, PROMPT_VERSION
from app.products.lifeos_coach.policies import enforce_medical_disclaimer_policy
from app.products.lifeos_coach.schemas import (
    LifeOSRespondRequest,
    LifeOSRespondResponse,
    TokenUsage
)
from app.utils.text import validate_input_text

logger = logging.getLogger(__name__)

class LifeOSHealthCoachService:
    """Orchestrates habit analysis, metrics tracking, and wellness disclaimer checks."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        formatter: ResponseFormatter,
        memory: MemoryService
    ):
        self.provider = provider
        self.formatter = formatter
        self.memory = memory

    async def process_request(self, request: LifeOSRespondRequest, tenant_id: str = "default_tenant") -> LifeOSRespondResponse:
        """Processes a health query, constructs dynamic prompts, calls the LLM, and enforces policies."""
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        cleaned_text = validate_input_text(request.text)

        # 1. Load context profile
        learner_profile = await self.memory.get_learner_profile(
            user_id="default_user",
            product_id="lifeos_coach",
            tenant_id=tenant_id
        )

        # 2. Enforce context budget limits
        learner_profile, _ = enforce_context_budget(
            learner_profile=learner_profile,
            retrieved_examples=[],
            max_tokens=settings.MAX_DYNAMIC_CONTEXT_TOKENS
        )

        # 3. Assemble dynamic prompt
        prompt = build_prompt(
            learner_profile=learner_profile,
            user_input=cleaned_text
        )

        provider_name = getattr(self.provider, "__class__", {}).__name__
        model_name = getattr(self.provider, "model_name", "unknown-model")

        raw_content = ""
        input_tokens = 0
        output_tokens = 0
        cached_tokens = 0
        cost = 0.0

        try:
            # 4. Call Provider
            prov_res = await self.provider.generate_structured_response(
                prompt=prompt,
                system_prompt=""
            )
            raw_content = prov_res.raw_content
            input_tokens = prov_res.input_tokens
            output_tokens = prov_res.output_tokens
            cached_tokens = prov_res.cached_tokens
            cost = prov_res.estimated_cost_usd

            parsed_data = self.formatter.parse_llm_response(raw_content)
            
        except Exception as provider_err:
            logger.error(f"LifeOS provider error: {provider_err}. Constructing low-confidence fallback.")
            parsed_data = {
                "detected_metrics": {"sleep": None, "diet": None, "activity": None},
                "analysis": f"Health service fallback activated. Error: {str(provider_err)}",
                "recommendations": ["Consult a medical professional for advice."],
                "disclaimer_triggered": True
            }

        # 5. Normalize fields
        normalized = {
            "detected_metrics": parsed_data.get("detected_metrics", {"sleep": None, "diet": None, "activity": None}),
            "analysis": parsed_data.get("analysis", ""),
            "recommendations": parsed_data.get("recommendations", []),
            "disclaimer_triggered": bool(parsed_data.get("disclaimer_triggered", False))
        }

        # Ensure recommendations is a list of strings
        if not isinstance(normalized["recommendations"], list):
            normalized["recommendations"] = [str(normalized["recommendations"])]

        # 6. Apply wellness warning safety check policies
        normalized = enforce_medical_disclaimer_policy(cleaned_text, normalized)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            estimated_cost_usd=cost
        )

        response = LifeOSRespondResponse(
            response_id=request_id,
            detected_metrics=normalized["detected_metrics"],
            analysis=normalized["analysis"],
            recommendations=normalized["recommendations"],
            disclaimer_triggered=normalized["disclaimer_triggered"],
            prompt_version=PROMPT_VERSION,
            provider=provider_name,
            model=model_name,
            token_usage=usage,
            latency_ms=latency_ms
        )

        # Log observability structured logs (truncating for privacy)
        log_text_preview = cleaned_text[:20] + "..." if len(cleaned_text) > 20 else cleaned_text
        log_event = {
            "request_id": request_id,
            "provider": provider_name,
            "model": model_name,
            "product_id": "lifeos_coach",
            "latency_ms": response.latency_ms,
            "disclaimer_triggered": response.disclaimer_triggered,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cached_tokens": usage.cached_tokens,
            "estimated_cost_usd": usage.estimated_cost_usd,
            "text_preview": log_text_preview
        }
        log_structured_event(log_event)

        return response
