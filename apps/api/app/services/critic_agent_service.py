import logging
from app.services.source_grounding_service import SourceGroundingService
from typing import Dict, Any, List

logger = logging.getLogger("critic_agent")

class CriticAgentService:
    @classmethod
    def critique_grounding(
        cls,
        candidate_answer: str,
        citations: List[str]
    ) -> Dict[str, Any]:
        """
        Audits answer text using factual alignments.
        """
        logger.info("CriticAgent auditing candidate response...")
        
        # Build mock chunks for matching
        chunks = [
            {"document_id": "doc_1", "chunk_id": f"c_{i}", "chunk_summary": c}
            for i, c in enumerate(citations)
        ]
        
        grounded_data = SourceGroundingService.ground_response(candidate_answer, chunks)
        return {
            "is_grounded": grounded_data["grounded"],
            "citations_matched": len(grounded_data["citations"])
        }
