import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.hybrid_retrieval_service import HybridRetrievalService
from app.services.memory_retrieval_service import MemoryRetrievalService
from typing import Dict, Any, List

logger = logging.getLogger("retrieval_agent")

class RetrievalAgentService:
    @classmethod
    async def gather_context(
        cls,
        db: AsyncSession,
        user_id: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Gathers workspace documents and user facts.
        """
        logger.info(f"RetrievalAgent gathering facts for: '{query}'")
        
        # 1. Workspace documents lookup
        workspace_chunks = []
        try:
            workspace_chunks = await HybridRetrievalService.retrieve(db, user_id, query)
        except Exception as e:
            logger.error(f"Workspace retrieval failed: {e}")

        # 2. User profile facts lookup
        user_facts = []
        try:
            user_facts = await MemoryRetrievalService.retrieve_relevant_facts(db, user_id, query)
        except Exception as e:
            logger.error(f"User memory retrieval failed: {e}")

        return {
            "workspace_context": [c.get("chunk_summary", "") for c in workspace_chunks],
            "user_preferences": user_facts
        }
