import sys
import os
from typing import Dict, Any

# Ensure .agents root directory is dynamically on python path
agents_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.agents"))
if agents_path not in sys.path:
    sys.path.insert(0, agents_path)

from agentEnglish.runtime import run_agent
from agentEnglish.schemas import AgentRequest
from .preview_guardrails import PreviewGuardrails
from .preview_budget_service import PreviewBudgetService

class AgentEnglishService:
    @classmethod
    async def respond_to_preview(cls, session_id: str, message: str) -> Dict[str, Any]:
        # 1. Enforce guardrails
        block_reason = PreviewGuardrails.check_limits(session_id)
        if block_reason:
            return {
                "message": block_reason,
                "tokens_used": 0,
                "cost": 0.0,
                "status": "blocked"
            }

        # 2. Prepare request
        req = AgentRequest(session_id=session_id, message=message)
        
        # 3. Call agentEnglish runtime in preview mode
        response = await run_agent(req, is_preview=True)
        
        # 4. Increment budget metrics on success
        if response.status == "success":
            PreviewBudgetService.increment_session(
                session_id, 
                response.tokens_used, 
                response.cost_usd
            )
            
        return {
            "message": response.message,
            "tokens_used": response.tokens_used,
            "cost": response.cost_usd,
            "status": response.status
        }

    @classmethod
    async def respond_to_authenticated(cls, session_id: str, message: str) -> Dict[str, Any]:
        # Authenticated users get unrestricted runtime behavior (is_preview=False)
        req = AgentRequest(session_id=session_id, message=message)
        response = await run_agent(req, is_preview=False)
        return {
            "message": response.message,
            "tokens_used": response.tokens_used,
            "cost": response.cost_usd,
            "status": response.status
        }
