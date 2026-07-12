import logging
import uuid
import time
from typing import Dict, Any, Optional, Tuple

from app.core.config import settings
from app.providers.base import BaseLLMProvider, ProviderResponse
from app.services.language_detector import LanguageDetector
from app.services.intent_classifier import IntentClassifier
from app.services.response_formatter import ResponseFormatter
from app.services.memory_service import MemoryService
from app.services.feedback_service import FeedbackService
from app.services.context_budget import enforce_context_budget
from app.prompts.prompt_library import estimate_token_count
from app.core.log_config import log_structured_event

# Product-specific imports
from app.products.english_coach.prompt_config import build_prompt, PROMPT_VERSION, STABLE_OUTPUT_SCHEMA_INSTRUCTIONS
from app.products.english_coach.policies import enforce_coaching_policies
from app.products.english_coach.schemas import (
    CoachRespondRequest,
    CoachRespondResponse,
    TokenUsage
)
from app.utils.text import validate_input_text

logger = logging.getLogger(__name__)

class EnglishCoachService:
    """Orchestrates query evaluations, translation corrections, and response generation for Prakash."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        detector: LanguageDetector,
        classifier: IntentClassifier,
        formatter: ResponseFormatter,
        memory: MemoryService
    ):
        self.provider = provider
        self.detector = detector
        self.classifier = classifier
        self.formatter = formatter
        self.memory = memory

    def _detect_ambiguity_heuristically(self, text: str) -> Tuple[bool, Optional[str]]:
        """Determines if the text input is too short or semantically ambiguous."""
        words = text.lower().split()
        if len(words) < 3:
            return True, "Your input is too short to coach. Could you please provide more context?"
            
        ambiguity_markers = ["usko bol", "use bol", "unhe bol", "bol dena", "bol do", "kar dena", "kar do", "use de dena", "use de do"]
        text_lower = text.lower()
        if any(marker in text_lower for marker in ambiguity_markers):
            if len(words) < 6:
                return True, "Who does 'usko/use' refer to, or what exact message should be conveyed? Please clarify."
                
        return False, None

    async def process_request(self, request: CoachRespondRequest, tenant_id: str = "default_tenant") -> CoachRespondResponse:
        """Processes query inputs, estimates token sizes, calls the LLM, and formats metrics."""
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # 1. Clean input
        cleaned_text = validate_input_text(request.text)

        # 2. Local fallback classifications
        local_style = self.detector.detect(cleaned_text)
        local_intent = self.classifier.classify(cleaned_text)

        # 3. Local ambiguity detection
        local_ambiguity, local_question = self._detect_ambiguity_heuristically(cleaned_text)

        # 4. Recall context profile and approved training examples
        learner_profile = await self.memory.get_learner_profile(
            user_id="default_user",
            product_id="english_coach",
            tenant_id=tenant_id
        )
        retrieved_examples = await self.memory.retrieve_examples(
            query=cleaned_text,
            product_id="english_coach"
        )

        # 5. Enforce token budget limits
        learner_profile, retrieved_examples = enforce_context_budget(
            learner_profile=learner_profile,
            retrieved_examples=retrieved_examples,
            max_tokens=settings.MAX_DYNAMIC_CONTEXT_TOKENS
        )

        # 6. Assemble dynamic prompt
        prompt = build_prompt(
            learner_profile=learner_profile,
            retrieved_examples=retrieved_examples,
            user_input=cleaned_text
        )

        provider_name = getattr(self.provider, "__class__", {}).__name__
        model_name = getattr(self.provider, "model_name", "unknown-model")

        raw_content = ""
        input_tokens = 0
        output_tokens = 0
        cached_tokens = 0
        cost = 0.0

        # 7. Execute LLM call with a single format repair pass
        try:
            prov_res = await self.provider.generate_structured_response(
                prompt=prompt,
                system_prompt=""
            )
            raw_content = prov_res.raw_content
            input_tokens = prov_res.input_tokens
            output_tokens = prov_res.output_tokens
            cached_tokens = prov_res.cached_tokens
            cost = prov_res.estimated_cost_usd

            try:
                parsed_data = self.formatter.parse_llm_response(raw_content)
            except ValueError as parse_err:
                logger.warning(f"Formatting check failed on V1. Retrying repair loop: {parse_err}")
                
                repair_prompt = (
                    f"The previous output failed JSON parsing with error: {parse_err}.\n"
                    f"Format the content correctly. Return ONLY raw valid JSON conforming to the schema:\n"
                    f"{STABLE_OUTPUT_SCHEMA_INSTRUCTIONS}\n\n"
                    f"Invalid output content was:\n{raw_content}"
                )
                prov_res_repair = await self.provider.generate_structured_response(
                    prompt=repair_prompt,
                    system_prompt=""
                )
                raw_content = prov_res_repair.raw_content
                
                input_tokens += prov_res_repair.input_tokens
                output_tokens += prov_res_repair.output_tokens
                cached_tokens += prov_res_repair.cached_tokens
                cost += prov_res_repair.estimated_cost_usd

                parsed_data = self.formatter.parse_llm_response(raw_content)

            normalized = self.formatter.normalize_response(parsed_data, cleaned_text)
            
        except Exception as provider_err:
            logger.error(f"Provider connection error: {provider_err}. Constructing low-confidence fallback.")
            normalized = {
                "detected_input_style": local_style,
                "intent": local_intent,
                "natural_english": cleaned_text if not local_ambiguity else None,
                "professional_english": cleaned_text if not local_ambiguity else None,
                "explanation": f"Service fallback activated. Error: {str(provider_err)}",
                "ambiguity": local_ambiguity,
                "clarification_question": local_question,
                "mistake_tags": [],
                "confidence": 0.10
            }

        # 8. Apply tone and content policies checks
        normalized = enforce_coaching_policies(normalized)

        # Enforce heuristic checks if ambiguity is flagged
        if local_ambiguity:
            normalized["ambiguity"] = True
            normalized["clarification_question"] = local_question or normalized.get("clarification_question")
            normalized["natural_english"] = None
            normalized["professional_english"] = None
            normalized["confidence"] = min(normalized["confidence"], 0.80)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            estimated_cost_usd=cost
        )

        response = CoachRespondResponse(
            response_id=request_id,
            detected_input_style=normalized["detected_input_style"],
            intent=normalized["intent"],
            natural_english=normalized["natural_english"],
            professional_english=normalized["professional_english"],
            explanation=normalized["explanation"],
            ambiguity=normalized["ambiguity"],
            clarification_question=normalized["clarification_question"],
            mistake_tags=normalized["mistake_tags"],
            confidence=normalized["confidence"],
            prompt_version=PROMPT_VERSION,
            provider=provider_name,
            model=model_name,
            token_usage=usage,
            latency_ms=latency_ms
        )

        # Register transaction for the feedback loops database lookup
        FeedbackService.register_transaction(
            response_id=request_id,
            input_text=cleaned_text,
            natural_english=response.natural_english or "",
            professional_english=response.professional_english or "",
            tags=response.mistake_tags or [response.intent]
        )

        # Emit audit logs
        log_text_preview = cleaned_text[:20] + "..." if len(cleaned_text) > 20 else cleaned_text
        log_event = {
            "request_id": request_id,
            "provider": provider_name,
            "model": model_name,
            "intent": response.intent,
            "detected_input_style": response.detected_input_style,
            "latency_ms": response.latency_ms,
            "ambiguity": response.ambiguity,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cached_tokens": usage.cached_tokens,
            "estimated_cost_usd": usage.estimated_cost_usd,
            "text_preview": log_text_preview
        }
        log_structured_event(log_event)
        
        # Trigger background evaluation check asynchronously (non-blocking)
        from app.tasks.jobs import run_live_eval_check
        if settings.CELERY_ENABLED:
            run_live_eval_check.delay(request_id)
        else:
            from app.tasks.worker import BackgroundJobWorker
            BackgroundJobWorker.submit_job(run_live_eval_check, request_id)

        return response
