import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_memory_service import UserMemoryService
from typing import Dict, Any, List

logger = logging.getLogger("memory_retrieval_service")

class MemoryRetrievalService:
    @classmethod
    async def retrieve_relevant_facts(
        cls,
        db: AsyncSession,
        user_id: str,
        query: str
    ) -> List[str]:
        """
        Retrieves matching facts/preferences from the user profile memory.
        Filter and highlight specific weaknesses or goals if the user query references them.
        """
        profile = await UserMemoryService.get_profile(db, user_id)
        facts = []

        # Always retrieve tone, explanation style, and preferred language as base facts
        facts.append(f"Preferred interaction tone: {profile.tone}")
        facts.append(f"Explanation detail style: {profile.explanation_style}")
        facts.append(f"Preferred language: {profile.preferred_language}")
        facts.append(f"Target English mastery level: {profile.target_english_level}")

        query_lower = query.lower()

        # Context-dependent fact retrieval: Match weaknesses
        matched_weaknesses = [w for w in profile.weaknesses if w.lower() in query_lower]
        if matched_weaknesses:
            facts.append(f"User is currently practicing/improving on: {', '.join(matched_weaknesses)}")
        elif profile.weaknesses:
            # Fallback to general listing if generic practice query
            if "practice" in query_lower or "exercise" in query_lower or "weakness" in query_lower:
                facts.append(f"User's overall areas for improvement: {', '.join(profile.weaknesses)}")

        # Match goals
        matched_goals = [g for g in profile.goals if g.lower() in query_lower]
        if matched_goals:
            facts.append(f"User's active goal matching query context: {', '.join(matched_goals)}")
        elif profile.goals:
            if "goal" in query_lower or "target" in query_lower or "plan" in query_lower:
                facts.append(f"User's long-term workspace goals: {', '.join(profile.goals)}")

        return facts
