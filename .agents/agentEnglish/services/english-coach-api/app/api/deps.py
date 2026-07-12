from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.config import settings
from app.db.session import get_db

# Providers
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import MockLLMProvider
from app.providers.openai_provider import OpenAILLMProvider
from app.providers.gemini_provider import GeminiLLMProvider

# Repositories
from app.repositories.approved_examples import ApprovedExamplesRepository
from app.repositories.learner_profiles import LearnerProfilesRepository
from app.repositories.sessions import SessionsRepository
from app.repositories.messages import MessagesRepository
from app.repositories.product_configs import ProductConfigsRepository
from app.repositories.family_profiles import FamilyProfilesRepository
from app.repositories.tenants import TenantsRepository, ProductEntitlementsRepository
from app.repositories.memberships import MembershipsRepository
from app.repositories.usage_ledger import UsageLedgerRepository
from app.repositories.review_queue import ReviewQueueRepository
from app.repositories.prompt_versions import PromptVersionsRepository
from app.repositories.experiments import ExperimentsRepository
from app.repositories.knowledge_documents import KnowledgeDocumentsRepository
from app.repositories.knowledge_chunks import KnowledgeChunksRepository
from app.repositories.retrieval_logs import RetrievalLogsRepository
from app.repositories.feedback_examples import FeedbackExamplesRepository
from app.repositories.datasets import DatasetsRepository

# Services
from app.services.budget_guard import BudgetGuard
from app.services.handoff_service import HandoffService
from app.services.review_service import ReviewService
from app.services.prompt_registry import PromptRegistryService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import HybridRetrievalService
from app.services.dataset_registry import DatasetRegistryService
from app.repositories.checkins import CheckinRunsRepository

# Services
from app.services.language_detector import LanguageDetector
from app.services.intent_classifier import IntentClassifier
from app.services.response_formatter import ResponseFormatter
from app.services.memory_service import MemoryService
from app.services.feedback_service import FeedbackService

# Product Services
from app.products.english_coach.service import EnglishCoachService
from app.products.lifeos_coach.service import LifeOSHealthCoachService
from app.products.family_checkin.service import FamilyCheckinService

# Voice Services
from app.services.transcription_service import TranscriptionService
from app.services.tts_service import TTSService
from app.services.voice_service import VoiceService

# Singletons for lightweight detectors/formatters
_detector = LanguageDetector()
_classifier = IntentClassifier()
_formatter = ResponseFormatter()

# Singletons for stubs
_transcription_service = TranscriptionService()
_tts_service = TTSService()

# Fallback file repo for offline scripts and testing
_fallback_approved_repo = ApprovedExamplesRepository(filepath=settings.APPROVED_EXAMPLES_FILE)
_fallback_memory = MemoryService(approved_repo=_fallback_approved_repo)
_fallback_feedback = FeedbackService(approved_repo=_fallback_approved_repo)

def get_llm_provider() -> BaseLLMProvider:
    """Dependency resolver determining the active LLM provider from settings."""
    provider_name = settings.MODEL_PROVIDER.lower()
    
    if provider_name == "openai" and settings.OPENAI_API_KEY:
        return OpenAILLMProvider(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.MODEL_NAME,
            timeout=float(settings.REQUEST_TIMEOUT_SECONDS),
            max_retries=settings.MAX_RETRIES,
            max_completion_tokens=settings.MAX_COMPLETION_TOKENS
        )
    elif provider_name == "gemini" and settings.GEMINI_API_KEY:
        return GeminiLLMProvider(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.MODEL_NAME
        )
        
    return MockLLMProvider()

async def get_approved_repository(db: Optional[AsyncSession] = Depends(get_db)) -> ApprovedExamplesRepository:
    """Gets approved examples repo backed by the active database connection."""
    if db is None:
        db = None
    return ApprovedExamplesRepository(db_session=db, filepath=settings.APPROVED_EXAMPLES_FILE)

async def get_memory_service(
    db: Optional[AsyncSession] = Depends(get_db),
    approved_repo: ApprovedExamplesRepository = Depends(get_approved_repository)
) -> MemoryService:
    """Gets memory service using current DB session repositories."""
    if db is None:
        db = None
    if not isinstance(approved_repo, ApprovedExamplesRepository):
        approved_repo = await get_approved_repository(db)
    profiles_repo = LearnerProfilesRepository(db) if db else None
    return MemoryService(approved_repo=approved_repo, profiles_repo=profiles_repo)

async def get_coach_service(
    db: Optional[AsyncSession] = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider),
    approved_repo: ApprovedExamplesRepository = Depends(get_approved_repository)
) -> EnglishCoachService:
    """Returns the EnglishCoachService mapped to the active DB session."""
    if db is None:
        db = None
    if not isinstance(approved_repo, ApprovedExamplesRepository):
        approved_repo = await get_approved_repository(db)
    profiles_repo = LearnerProfilesRepository(db) if db else None
    memory = MemoryService(approved_repo=approved_repo, profiles_repo=profiles_repo)
    return EnglishCoachService(
        provider=provider,
        detector=_detector,
        classifier=_classifier,
        formatter=_formatter,
        memory=memory
    )

async def get_lifeos_coach_service(
    db: Optional[AsyncSession] = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider),
    approved_repo: ApprovedExamplesRepository = Depends(get_approved_repository)
) -> LifeOSHealthCoachService:
    """Returns the LifeOSHealthCoachService mapped to the active DB session."""
    if db is None:
        db = None
    if not isinstance(approved_repo, ApprovedExamplesRepository):
        approved_repo = await get_approved_repository(db)
    profiles_repo = LearnerProfilesRepository(db) if db else None
    memory = MemoryService(approved_repo=approved_repo, profiles_repo=profiles_repo)
    return LifeOSHealthCoachService(
        provider=provider,
        formatter=_formatter,
        memory=memory
    )

async def get_family_checkin_service(
    db: Optional[AsyncSession] = Depends(get_db),
    provider: BaseLLMProvider = Depends(get_llm_provider)
) -> FamilyCheckinService:
    """Returns the FamilyCheckinService mapped to the active DB session."""
    if db is None:
        db = None
    family_repo = FamilyProfilesRepository(db) if db else None
    checkin_repo = CheckinRunsRepository(db) if db else None
    return FamilyCheckinService(
        provider=provider,
        formatter=_formatter,
        family_repo=family_repo,
        checkin_repo=checkin_repo
    )

async def get_voice_service(
    coach_service: EnglishCoachService = Depends(get_coach_service)
) -> VoiceService:
    """Returns the VoiceService coordinator chained to the EnglishCoachService."""
    return VoiceService(
        transcription_service=_transcription_service,
        tts_service=_tts_service,
        coach_service=coach_service
    )

def get_feedback_service() -> FeedbackService:
    """Deprecated: returns the file-based feedback service for backward compatibility."""
    return _fallback_feedback

# Backward compatibility alias
CoachService = EnglishCoachService
_approved_repo = _fallback_approved_repo

async def get_tenants_repository(db: Optional[AsyncSession] = Depends(get_db)) -> TenantsRepository:
    return TenantsRepository(db)

async def get_entitlements_repository(db: Optional[AsyncSession] = Depends(get_db)) -> ProductEntitlementsRepository:
    return ProductEntitlementsRepository(db)

async def get_memberships_repository(db: Optional[AsyncSession] = Depends(get_db)) -> MembershipsRepository:
    return MembershipsRepository(db)

async def get_usage_ledger_repository(db: Optional[AsyncSession] = Depends(get_db)) -> UsageLedgerRepository:
    return UsageLedgerRepository(db)

async def get_review_queue_repository(db: Optional[AsyncSession] = Depends(get_db)) -> ReviewQueueRepository:
    return ReviewQueueRepository(db)

async def get_prompt_versions_repository(db: Optional[AsyncSession] = Depends(get_db)) -> PromptVersionsRepository:
    return PromptVersionsRepository(db)

async def get_experiments_repository(db: Optional[AsyncSession] = Depends(get_db)) -> ExperimentsRepository:
    return ExperimentsRepository(db)

async def get_budget_guard(
    db: Optional[AsyncSession] = Depends(get_db),
    ledger_repo: UsageLedgerRepository = Depends(get_usage_ledger_repository),
    tenant_repo: TenantsRepository = Depends(get_tenants_repository)
) -> BudgetGuard:
    return BudgetGuard(ledger_repo=ledger_repo, tenant_repo=tenant_repo)

async def get_handoff_service(
    review_repo: ReviewQueueRepository = Depends(get_review_queue_repository)
) -> HandoffService:
    return HandoffService(review_repo=review_repo)

async def get_review_service(
    review_repo: ReviewQueueRepository = Depends(get_review_queue_repository)
) -> ReviewService:
    return ReviewService(review_repo=review_repo)

async def get_prompt_registry(
    prompt_repo: PromptVersionsRepository = Depends(get_prompt_versions_repository),
    experiment_repo: ExperimentsRepository = Depends(get_experiments_repository)
) -> PromptRegistryService:
    return PromptRegistryService(prompt_repo=prompt_repo, experiment_repo=experiment_repo)

async def get_knowledge_documents_repository(db: Optional[AsyncSession] = Depends(get_db)) -> KnowledgeDocumentsRepository:
    return KnowledgeDocumentsRepository(db)

async def get_knowledge_chunks_repository(db: Optional[AsyncSession] = Depends(get_db)) -> KnowledgeChunksRepository:
    return KnowledgeChunksRepository(db)

async def get_retrieval_logs_repository(db: Optional[AsyncSession] = Depends(get_db)) -> RetrievalLogsRepository:
    return RetrievalLogsRepository(db)

async def get_feedback_examples_repository(db: Optional[AsyncSession] = Depends(get_db)) -> FeedbackExamplesRepository:
    return FeedbackExamplesRepository(db)

async def get_datasets_repository(db: Optional[AsyncSession] = Depends(get_db)) -> DatasetsRepository:
    return DatasetsRepository(db)

def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

async def get_retrieval_service(
    chunks_repo: KnowledgeChunksRepository = Depends(get_knowledge_chunks_repository),
    logs_repo: RetrievalLogsRepository = Depends(get_retrieval_logs_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> HybridRetrievalService:
    return HybridRetrievalService(chunks_repo=chunks_repo, logs_repo=logs_repo, embedding_service=embedding_service)

async def get_dataset_registry(
    datasets_repo: DatasetsRepository = Depends(get_datasets_repository),
    doc_repo: KnowledgeDocumentsRepository = Depends(get_knowledge_documents_repository),
    chunk_repo: KnowledgeChunksRepository = Depends(get_knowledge_chunks_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> DatasetRegistryService:
    return DatasetRegistryService(
        datasets_repo=datasets_repo,
        doc_repo=doc_repo,
        chunk_repo=chunk_repo,
        embedding_service=embedding_service
    )
