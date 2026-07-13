import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.memory_retrieval_service import MemoryRetrievalService
from app.services.session_memory_service import SessionMemoryService
from typing import Dict, Any, List, Optional

logger = logging.getLogger("memory_injection_service")

class MemoryInjectionService:
    @classmethod
    async def inject_memories_into_system_prompt(
        cls,
        db: AsyncSession,
        user_id: str,
        query: str,
        session_id: Optional[str] = None,
        base_prompt: str = ""
    ) -> str:
        """
        Retrieves relevant long-term and short-term memories and injects them into the system prompt.
        """
        # 1. Fetch relevant long-term facts
        facts = []
        try:
            facts = await MemoryRetrievalService.retrieve_relevant_facts(db, user_id, query)
        except Exception as e:
            logger.error(f"Error fetching profile facts for prompt injection: {e}")

        # 2. Fetch active session preferences if session_id is provided
        session_prefs = []
        if session_id:
            prefs = SessionMemoryService.get_all_session_preferences(session_id)
            for key, val in prefs.items():
                session_prefs.append(f"Session preference - {key}: {val}")

        # 3. Assemble memory block
        memory_blocks = []
        if facts:
            memory_blocks.append("Long-term User Memory & Preferences:")
            memory_blocks.extend([f" - {f}" for f in facts])
        
        if session_prefs:
            memory_blocks.append("Temporary Session Preferences:")
            memory_blocks.extend([f" - {p}" for p in session_prefs])

        if not memory_blocks:
            return base_prompt

        memory_context = "\n".join(memory_blocks)
        separator = "\n" if base_prompt else ""
        
        # Inject memory prefix
        injected_prompt = (
            f"=== USER MEMORY GATEWAY ===\n"
            f"{memory_context}\n"
            f"============================\n"
            f"{separator}{base_prompt}"
        )
        return injected_prompt
