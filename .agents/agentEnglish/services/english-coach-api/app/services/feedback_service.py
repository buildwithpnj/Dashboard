import logging
from datetime import datetime
import uuid
from typing import Dict, Any, List

from app.schemas.coach import CoachFeedbackRequest, CoachFeedbackResponse
from app.schemas.evals import ApprovedExample
from app.repositories.approved_examples import ApprovedExamplesRepository

logger = logging.getLogger(__name__)

class FeedbackService:
    """Manages transaction memory states and appends approved signals to database files."""

    # In-memory transaction cache to link feedback UUIDs back to source strings
    _transaction_registry: Dict[str, Dict[str, Any]] = {}

    def __init__(self, approved_repo: ApprovedExamplesRepository):
        self.approved_repo = approved_repo

    @classmethod
    def register_transaction(
        cls,
        response_id: str,
        input_text: str,
        natural_english: str,
        professional_english: str,
        tags: List[str]
    ) -> None:
        """Saves a temporary record of the transaction in the in-memory cache."""
        cls._transaction_registry[response_id] = {
            "input_text": input_text,
            "natural_english": natural_english,
            "professional_english": professional_english,
            "tags": tags
        }

    async def record_feedback(self, request: CoachFeedbackRequest) -> CoachFeedbackResponse:
        """Processes user feedback.
        
        Saves approved corrections to the approved examples JSONL repository.
        """
        response_id = request.response_id
        tx = self._transaction_registry.get(response_id)

        if not tx:
            logger.warning(f"Transaction ID {response_id} not found in temporary cache. Feedback ignored.")
            return CoachFeedbackResponse(
                status="ignored",
                message="Feedback ignored: Response transaction ID not found or already processed."
            )

        # Remove from transaction registry once processed
        self._transaction_registry.pop(response_id, None)

        # Decide if we want to save this example (if approved or user has manually corrected it)
        if request.approved or request.corrected_text:
            natural = request.corrected_text if request.corrected_text else tx["natural_english"]
            professional = tx["professional_english"]
            
            # Ensure we have valid string inputs to inject
            if not natural:
                natural = tx["natural_english"] or tx["input_text"]
            if not professional:
                professional = tx["professional_english"] or natural

            # Construct example structure
            example = ApprovedExample(
                id=f"app_{str(uuid.uuid4())[:8]}",
                input_text=tx["input_text"],
                natural_english=natural,
                professional_english=professional,
                tags=tx["tags"],
                created_at=datetime.utcnow().isoformat() + "Z"
            )

            # Persist back to database repository file
            await self.approved_repo.add_example(example)
            logger.info(f"Persisted feedback correction. Example ID={example.id} tagged with {example.tags}.")

            return CoachFeedbackResponse(
                status="success",
                message="Feedback captured successfully. Correction learning signals stored in persistent database."
            )

        return CoachFeedbackResponse(
            status="success",
            message="Feedback processed. Disapproved signals noted without persistence."
        )
