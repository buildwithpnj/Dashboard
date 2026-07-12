import pytest
import uuid
import json
from app.db.session import AsyncSessionLocal
from app.db.models import KnowledgeDocument, KnowledgeChunk
from app.repositories.knowledge_documents import KnowledgeDocumentsRepository
from app.repositories.knowledge_chunks import KnowledgeChunksRepository
from app.repositories.retrieval_logs import RetrievalLogsRepository
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import HybridRetrievalService

@pytest.mark.anyio
async def test_tenant_scoped_similarity_retrieval():
    """Asserts that search results strictly return chunks matching the caller's tenant."""
    async with AsyncSessionLocal() as db:
        doc_repo = KnowledgeDocumentsRepository(db)
        chunk_repo = KnowledgeChunksRepository(db)
        logs_repo = RetrievalLogsRepository(db)
        emb_service = EmbeddingService()
        
        tenant_a = f"tenant-a-{uuid.uuid4()}"
        tenant_b = f"tenant-b-{uuid.uuid4()}"
        
        # 1. Create Tenant A document & chunk
        doc_a = KnowledgeDocument(id="doc-a", tenant_id=tenant_a, product_id="english_coach", name="Doc A", source_type="txt")
        await doc_repo.create(doc_a)
        
        chunk_a = KnowledgeChunk(
            id="chunk-a",
            doc_id="doc-a",
            tenant_id=tenant_a,
            product_id="english_coach",
            content="This is Prakash's confidential data matching Tenant A context query.",
            embedding_json=json.dumps([0.05] * 1536)
        )
        await chunk_repo.create(chunk_a)

        # 2. Create Tenant B document & chunk
        doc_b = KnowledgeDocument(id="doc-b", tenant_id=tenant_b, product_id="english_coach", name="Doc B", source_type="txt")
        await doc_repo.create(doc_b)
        
        chunk_b = KnowledgeChunk(
            id="chunk-b",
            doc_id="doc-b",
            tenant_id=tenant_b,
            product_id="english_coach",
            content="Confidential record matching Tenant B only.",
            embedding_json=json.dumps([0.05] * 1536)
        )
        await chunk_repo.create(chunk_b)
        await db.commit()

        # 3. Search under Tenant A context
        service = HybridRetrievalService(chunk_repo, logs_repo, emb_service)
        results = await service.retrieve(
            tenant_id=tenant_a,
            product_id="english_coach",
            query="confidential data",
            limit=3,
            threshold=0.0
        )
        
        # Verify isolation: should only return Tenant A's chunk
        assert len(results) == 1
        assert results[0]["id"] == "chunk-a"
        assert "Tenant A" in results[0]["content"]

        # Cleanup
        await chunk_repo.delete(chunk_a)
        await chunk_repo.delete(chunk_b)
        await doc_repo.delete(doc_a)
        await doc_repo.delete(doc_b)
        await db.commit()
