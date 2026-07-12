import logging
import uuid
import time
import json
import datetime
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.providers.base import BaseLLMProvider, ProviderResponse
from app.services.response_formatter import ResponseFormatter
from app.core.log_config import log_structured_event

# Database Model Imports
from app.db.models import FamilyProfile, CheckinRun

# Repository Imports
from app.repositories.family_profiles import FamilyProfilesRepository
from app.repositories.checkins import CheckinRunsRepository

# Product Specific Imports
from app.products.family_checkin.prompt_config import build_prompt, PROMPT_VERSION
from app.products.family_checkin.policies import enforce_family_escalation_policy
from app.products.family_checkin.schemas import (
    FamilyCheckinRequest,
    FamilyCheckinResponse,
    ContactInfo,
    TokenUsage
)
from app.utils.text import validate_input_text

logger = logging.getLogger(__name__)

class FamilyCheckinService:
    """Manages check-in triggers, script stages, safety escalations, and persists results to database."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        formatter: ResponseFormatter,
        family_repo: FamilyProfilesRepository,
        checkin_repo: CheckinRunsRepository
    ):
        self.provider = provider
        self.formatter = formatter
        self.family_repo = family_repo
        self.checkin_repo = checkin_repo

    async def process_request(self, request: FamilyCheckinRequest, tenant_id: str = "default_tenant") -> FamilyCheckinResponse:
        """Evaluates parent messages, checks safety boundaries, alerts contacts, and commits results."""
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        cleaned_text = validate_input_text(request.message_text)

        # 1. Retrieve or construct Family Profile from repository database
        profile_db_id = f"{tenant_id}_{request.user_id}"
        profile = await self.family_repo.get_by_id_and_tenant(profile_db_id, tenant_id=tenant_id)
        if not profile:
            # Create a default configuration for Prakash's mom if database is unseeded
            profile = FamilyProfile(
                id=profile_db_id,
                parent_name="Mom",
                tenant_id=tenant_id,
                preferred_language="Hindi",
                escalation_contacts_json=json.dumps([
                    {"name": "Prakash", "phone": "+91-9876543210", "relationship": "Son"}
                ]),
                script_stage="wellness_check"
            )
            await self.family_repo.create(profile)

        # Extract contacts
        try:
            contacts_list = json.loads(profile.escalation_contacts_json)
        except Exception:
            contacts_list = [{"name": "Prakash", "phone": "+91-9876543210", "relationship": "Son"}]

        contacts = [ContactInfo(**c) for c in contacts_list]

        # 2. Assemble prompt template
        prompt = build_prompt(
            parent_name=profile.parent_name,
            preferred_language=profile.preferred_language,
            script_stage=profile.script_stage,
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
            # 3. Query LLM provider
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
            logger.error(f"Family check-in provider error: {provider_err}. Constructing fallback escalation.")
            parsed_data = {
                "checkin_status": "escalated",
                "response_text": "मदद के लिए कृपया तुरंत संपर्क करें।",
                "notes": f"Fallback triggered. Error: {str(provider_err)}",
                "escalation_triggered": True
            }

        # 4. Normalize response
        normalized = {
            "checkin_status": str(parsed_data.get("checkin_status", "normal")),
            "response_text": str(parsed_data.get("response_text", "")),
            "notes": parsed_data.get("notes"),
            "escalation_triggered": bool(parsed_data.get("escalation_triggered", False))
        }

        # 5. Apply safety check policies
        normalized = enforce_family_escalation_policy(cleaned_text, normalized)

        # 6. Save CheckinRun records to database repository
        run_record = CheckinRun(
            id=request_id,
            user_id=request.user_id,
            tenant_id=tenant_id,
            session_id=request.session_id or f"sess-{request_id}",
            status=normalized["checkin_status"],
            escalated_at=datetime.datetime.utcnow() if normalized["escalation_triggered"] else None,
            notes=normalized["notes"]
        )
        await self.checkin_repo.create(run_record)

        # Trigger background safety followup scan (durable Celery if enabled)
        from app.core.config import settings
        from app.tasks.jobs import family_checkin_followup_task
        if settings.CELERY_ENABLED:
            family_checkin_followup_task.delay(request.user_id, request_id, tenant_id)
        else:
            from app.tasks.worker import BackgroundJobWorker
            BackgroundJobWorker.submit_job(family_checkin_followup_task, request.user_id, request_id, tenant_id)

        # If escalated, we can log alerts
        if normalized["escalation_triggered"]:
            logger.error(f"Wellness Escalation Triggered for {request.user_id}. Alerting contacts: {contacts_list}")

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            estimated_cost_usd=cost
        )

        response = FamilyCheckinResponse(
            response_id=request_id,
            checkin_status=normalized["checkin_status"],
            response_text=normalized["response_text"],
            notes=normalized["notes"],
            escalation_triggered=normalized["escalation_triggered"],
            escalation_contacts=contacts,
            prompt_version=PROMPT_VERSION,
            provider=provider_name,
            model=model_name,
            token_usage=usage,
            latency_ms=latency_ms
        )

        # Observability logs (truncating for privacy)
        log_text_preview = cleaned_text[:20] + "..." if len(cleaned_text) > 20 else cleaned_text
        log_event = {
            "request_id": request_id,
            "provider": provider_name,
            "model": model_name,
            "product_id": "family_checkin",
            "latency_ms": response.latency_ms,
            "escalation_triggered": response.escalation_triggered,
            "checkin_status": response.checkin_status,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cached_tokens": usage.cached_tokens,
            "estimated_cost_usd": usage.estimated_cost_usd,
            "text_preview": log_text_preview
        }
        log_structured_event(log_event)

        return response
