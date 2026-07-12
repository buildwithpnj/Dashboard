import asyncio
import json
import logging
from app.db.session import engine, AsyncSessionLocal
from app.db.models import Base, ProductConfig, LearnerProfile, ApprovedExample, FamilyProfile

# Configure basic logging to see print outputs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    logger.info("Initializing database schemas...")
    
    # 1. Reset/re-create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        logger.info("Seeding product configs...")
        configs = [
            ProductConfig(
                id="english_coach",
                name="Warborn English Coach",
                description="Translates and corrects English, Hindi, and Hinglish updates.",
                prompt_template="Default english coach instructions.",
                max_dynamic_tokens=500
            ),
            ProductConfig(
                id="lifeos_coach",
                name="LifeOS Health Coach",
                description="Habits tracker assessing diet, sleep, and activity.",
                prompt_template="Default health coach instructions.",
                max_dynamic_tokens=400
            ),
            ProductConfig(
                id="family_checkin",
                name="Family Parent Check-in",
                description="Conducts safety wellness check-ins on family members.",
                prompt_template="Default family checkin instructions.",
                max_dynamic_tokens=300
            )
        ]
        session.add_all(configs)

        logger.info("Seeding default learner profile...")
        profile = LearnerProfile(
            id="default_user_english_coach",
            user_id="default_user",
            product_id="english_coach",
            summary="Prakash is a senior software engineer who writes and speaks English daily. He wants to communicate naturally, clearly, and authoritatively.",
            metadata_json="{}"
        )
        session.add(profile)

        logger.info("Seeding default family profiles...")
        family = FamilyProfile(
            id="default_user",
            parent_name="Mom",
            preferred_language="Hindi",
            escalation_contacts_json=json.dumps([
                {"name": "Prakash", "phone": "+91-9876543210", "relationship": "Son"}
            ]),
            script_stage="wellness_check"
        )
        session.add(family)

        logger.info("Seeding base approved coaching examples...")
        ex = ApprovedExample(
            id="app_01",
            product_id="english_coach",
            input_text="i am not able to join because network issue tha",
            natural_english="I was unable to join because of a network issue.",
            professional_english="I could not attend the meeting due to connectivity problems.",
            tags_json=json.dumps(["correction", "english_coach"])
        )
        session.add(ex)

        await session.commit()
    logger.info("Database seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed())
