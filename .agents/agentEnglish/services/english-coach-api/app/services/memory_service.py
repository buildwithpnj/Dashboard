from typing import List, Optional
from app.repositories.approved_examples import ApprovedExamplesRepository
from app.repositories.learner_profiles import LearnerProfilesRepository

class MemoryService:
    """Shared context retrieval service managing profile contexts and matched approved examples."""

    def __init__(
        self,
        approved_repo: ApprovedExamplesRepository,
        profiles_repo: Optional[LearnerProfilesRepository] = None
    ):
        self.approved_repo = approved_repo
        self.profiles_repo = profiles_repo

    async def get_learner_profile(self, user_id: str, product_id: str, tenant_id: str = "default_tenant") -> str:
        """Loads user settings preferences or outputs stable context fallbacks."""
        if self.profiles_repo:
            profile = await self.profiles_repo.get_by_user_and_product(user_id, product_id, tenant_id=tenant_id)
            if profile:
                return profile.summary

        # Default fallback profile
        return (
            "Prakash is a professional engineer who communicates with global clients. "
            "He wants to sound natural, polite, and authoritative, avoiding bookish "
            "or robotic English."
        )

    async def retrieve_examples(self, query: str, product_id: str = "english_coach", limit: int = 3) -> List[str]:
        """Retrieves and formats matching approved training pairs from the persistence database."""
        query_lower = query.lower()
        
        # Load examples for target product
        all_examples = await self.approved_repo.get_all(product_id=product_id)
        
        matched = []
        
        # 1. Search for keyword intersection matching
        query_words = {w.strip(".,?!;:()\"'") for w in query_lower.split() if len(w) > 2}
        
        for ex in all_examples:
            ex_words = {w.strip(".,?!;:()\"'") for w in ex.input_text.lower().split()}
            if query_words.intersection(ex_words):
                matched.append(ex)
                
        # 2. Append general exemplars if search yields less than limit
        if len(matched) < limit:
            for ex in all_examples:
                if ex not in matched:
                    matched.append(ex)
                    if len(matched) >= limit:
                        break

        # Format examples into compact strings
        formatted = []
        for ex in matched[:limit]:
            formatted.append(
                f"Input: '{ex.input_text}' -> Natural: '{ex.natural_english}' | Professional: '{ex.professional_english}'"
            )
            
        return formatted
