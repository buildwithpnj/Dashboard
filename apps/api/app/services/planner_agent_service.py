import logging
from typing import Dict, Any, List

logger = logging.getLogger("planner_agent")

class PlannerAgentService:
    @classmethod
    def create_plan(cls, query: str) -> List[Dict[str, Any]]:
        """
        Decomposes query into planning steps.
        """
        logger.info(f"PlannerAgent creating steps for: '{query}'")
        
        # Deconstruct query into generic actions
        query_lower = query.lower()
        if "note" in query_lower:
            return [
                {"step": 1, "agent": "retrieval", "action": "fetch_workspace_context"},
                {"step": 2, "agent": "action", "action": "create_lesson_note"}
            ]
        elif "task" in query_lower or "goal" in query_lower:
            return [
                {"step": 1, "agent": "retrieval", "action": "fetch_user_preferences"},
                {"step": 2, "agent": "action", "action": "create_goal_task"}
            ]
        else:
            return [
                {"step": 1, "agent": "retrieval", "action": "fetch_hybrid_sources"},
                {"step": 2, "agent": "critic", "action": "verify_factual_grounding"}
            ]
