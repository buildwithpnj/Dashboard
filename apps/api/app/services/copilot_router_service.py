import logging
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.copilot_context_payload import CopilotContextPayload
from app.services.page_context_service import PageContextService
from app.services.llm_provider_router import LLMProviderRouter
from app.services.hybrid_retrieval_service import HybridRetrievalService

logger = logging.getLogger("copilot_router_service")

# Route-specific system prompt expansions
_ROUTE_HINTS: Dict[str, str] = {
    "finance":   "The user is on the Finance page. You can help with budgets, transactions, account balances, and spending trends.",
    "habits":    "The user is on the Habits tracker. You can help with streak analysis, habit consistency, and goal planning.",
    "aicoach":   "The user is on the AI Coach page. You can help with personal development insights and learning recommendations.",
    "notes":     "The user is on the Notes page. You can help create, search, or summarise lesson notes and knowledge entries.",
    "books":     "The user is on the Books page. You can help track reading progress, summarise books, or recommend titles.",
    "recovery":  "The user is on the Recovery tracking page. You can help monitor sobriety streaks and wellness goals.",
    "dashboard": "The user is on the main dashboard. You can help navigate to any module, summarise their day, or answer general questions about Warborn OS.",
    "storage":   "The user is on the Storage page. You can help manage cloud drives and file syncing.",
}

_SYSTEM_PROMPT = """You are Warborn Copilot, an intelligent personal AI assistant embedded in Warborn OS — a personal productivity operating system.

You are context-aware: you know which page the user is on and can take relevant actions.
You are concise, helpful, and conversational. Respond naturally like a smart assistant, not a robot.
Never echo back the user's message verbatim. Always provide a real, useful response.
If the user's question references documents, knowledge, or their workspace data, use the provided Reference Data section to answer accurately.
If you don't know something or it is not in the reference data, say so honestly.
Keep replies under 3 sentences unless the user asks for detail."""


class CopilotRouterService:
    @classmethod
    async def process_query(
        cls,
        db: AsyncSession,
        query: str,
        ctx: CopilotContextPayload,
        user_id: str,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Sends query to LLM (via LLMProviderRouter) with full route context, retrieved RAG documents, and chat history.
        Returns (reply_text, suggested_action).
        """
        route = (ctx.current_route or "/dashboard").lower()

        # Build route-aware system prompt
        route_hint = ""
        for key, hint in _ROUTE_HINTS.items():
            if key in route:
                route_hint = hint
                break
        if not route_hint:
            route_hint = _ROUTE_HINTS["dashboard"]

        # 1. Retrieve relevant knowledge chunks matching user's query
        rag_context = ""
        try:
            chunks = await HybridRetrievalService.retrieve(db, user_id, query)
            if chunks:
                logger.info(f"Retrieved {len(chunks)} knowledge chunks for Copilot query: '{query}'")
                context_blocks = []
                for i, chunk in enumerate(chunks[:3]):  # Use top 3 matching chunks
                    text = chunk.get("chunk_text") or chunk.get("chunk_summary") or ""
                    context_blocks.append(f"[Document {i+1}]: {text}")
                rag_context = "\n\n".join(context_blocks)
        except Exception as e:
            logger.error(f"Failed to retrieve RAG knowledge chunks for user {user_id}: {e}")

        # Assemble prompt
        system_content = f"{_SYSTEM_PROMPT}\n\nCurrent context: {route_hint}"
        if rag_context:
            system_content += f"\n\nReference Data from User's Workspace:\n{rag_context}"

        from app.services.memory_injection_service import MemoryInjectionService
        system_content = await MemoryInjectionService.inject_memories_into_system_prompt(
            db=db,
            user_id=user_id,
            query=query,
            session_id=None,
            base_prompt=system_content
        )

        # Build message list: system + rolling history + current user message
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]

        if history:
            # Include last 6 turns max to stay within context budget
            for entry in history[-6:]:
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": query})

        # Call LLM
        try:
            result = await LLMProviderRouter.route_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=512
            )

            if result.get("status") == "success":
                reply_text = result.get("content", "I'm not sure how to help with that.")
            else:
                logger.warning(f"LLM returned error: {result.get('message')}")
                reply_text = "I'm having trouble connecting to my AI brain right now. Please try again in a moment."

        except Exception as e:
            logger.error(f"CopilotRouterService LLM call failed: {e}")
            reply_text = "Something went wrong on my end. Please try again."

        # Detect simple action intents
        query_lower = query.lower()
        suggested_action: Dict[str, Any] = {}

        if "create" in query_lower and "note" in query_lower:
            suggested_action = {
                "action_name": "create_lesson_note",
                "payload": {"title": "Copilot Note", "content": reply_text}
            }
        elif "navigate" in query_lower or "go to" in query_lower:
            suggested_action = {"action_name": "navigate_dashboard", "payload": {"target": "/dashboard"}}

        return reply_text, suggested_action
