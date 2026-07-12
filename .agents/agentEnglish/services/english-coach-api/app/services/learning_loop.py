import uuid
from app.db.models import FeedbackExample
from app.repositories.feedback_examples import FeedbackExamplesRepository

class LearningLoopService:
    """Manages the learning flywheel, transforming manual ops reviews into structured memory examples."""

    def __init__(self, feedback_repo: FeedbackExamplesRepository):
        self.feedback_repo = feedback_repo

    async def register_feedback(
        self,
        tenant_id: str,
        product_id: str,
        input_text: str,
        output_text: str,
        is_positive: bool = True
    ) -> FeedbackExample:
        """Ingests positive or negative prompt templates runs into memory storage."""
        example = FeedbackExample(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            product_id=product_id,
            input_text=input_text,
            output_text=output_text,
            status="positive" if is_positive else "negative"
        )
        await self.feedback_repo.create(example)
        await self.feedback_repo.db.commit()
        return example
