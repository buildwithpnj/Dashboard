import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.planner_agent_service import PlannerAgentService
from app.services.retrieval_agent_service import RetrievalAgentService
from app.services.action_agent_service import ActionAgentService
from app.services.critic_agent_service import CriticAgentService
from app.services.agent_handoff_service import AgentHandoffService
from typing import Dict, Any, List

logger = logging.getLogger("agent_coordinator")

class AgentCoordinatorService:
    @classmethod
    async def coordinate_multi_agent_run(
        cls,
        db: AsyncSession,
        user_id: str,
        query: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinates specialized agent handoffs and executes multi-step task flows.
        """
        logger.info(f"Coordinator starting multi-agent loop for: '{query}'")
        
        # 1. Planner Agent
        plan = PlannerAgentService.create_plan(query)
        trace_history = []
        shared_state = {"query": query, "payload": payload, "plan": plan}

        # 2. Retrieve, Action, or Critique Step Loops
        for step in plan:
            agent = step["agent"]
            action = step["action"]
            
            # Step Transition Frame
            frame = AgentHandoffService.create_handoff_frame(
                sender="coordinator",
                recipient=agent,
                state=shared_state
            )
            
            if agent == "retrieval":
                ctx = await RetrievalAgentService.gather_context(db, user_id, query)
                shared_state["workspace_context"] = ctx["workspace_context"]
                shared_state["user_preferences"] = ctx["user_preferences"]
                
                # Verify transition keys
                AgentHandoffService.verify_state_transition(frame, ["workspace_context", "user_preferences"])
                trace_history.append(f"Handoff to Retrieval: Context and profile loaded successfully.")
                
            elif agent == "action":
                success, msg = await ActionAgentService.execute_action(
                    db, user_id, action, payload
                )
                shared_state["action_success"] = success
                shared_state["action_message"] = msg
                
                AgentHandoffService.verify_state_transition(frame, ["action_success"])
                trace_history.append(f"Handoff to Action: Executed '{action}' with result success={success}.")
                
            elif agent == "critic":
                citations = shared_state.get("workspace_context", [])
                candidate = shared_state.get("action_message", "No answer formulated.")
                
                audit = CriticAgentService.critique_grounding(candidate, citations)
                shared_state["audit_result"] = audit
                
                AgentHandoffService.verify_state_transition(frame, ["audit_result"])
                trace_history.append(f"Handoff to Critic: Grounding verified is_grounded={audit['is_grounded']}.")

        return {
            "status": "success",
            "plan": plan,
            "final_state": shared_state,
            "trace_history": trace_history
        }
