import uuid
import json
from typing import List, Dict, Any, Optional
from app.repositories.knowledge_chunks import KnowledgeChunksRepository
from app.repositories.retrieval_logs import RetrievalLogsRepository
from app.services.embedding_service import EmbeddingService
from app.services.reranker import SimpleReranker
from app.db.models import RetrievalLog

class HybridRetrievalService:
    """Retrieves document chunks using semantic similarity lookups and lexical overlap rerankings."""

    def __init__(
        self,
        chunks_repo: KnowledgeChunksRepository,
        logs_repo: RetrievalLogsRepository,
        embedding_service: EmbeddingService
    ):
        self.chunks_repo = chunks_repo
        self.logs_repo = logs_repo
        self.embedding_service = embedding_service

    async def retrieve(
        self,
        tenant_id: str,
        product_id: str,
        query: str,
        limit: int = 5,
        threshold: float = 0.5,
        max_context_tokens: int = 400
    ) -> List[Dict[str, Any]]:
        """Finds similarity matches, applies rerank orders, logs transactions, and respects token budgets."""
        if not query or not query.strip():
            return []

        # 1. Generate text embedding
        query_vector = await self.embedding_service.get_embedding(query)

        # 2. Retrieve candidates
        candidates = await self.chunks_repo.search_similar_chunks(
            tenant_id=tenant_id,
            product_id=product_id,
            query_embedding=query_vector,
            limit=limit * 2,
            threshold=threshold
        )

        # 3. Apply hybrid lexical reranker
        reranked = SimpleReranker.rerank(query, candidates)

        # 4. Enforce context budget tokens limit
        retrieved = []
        tokens = 0
        for item in reranked:
            approx = len(item["content"].split(" "))
            if tokens + approx > max_context_tokens:
                continue
            tokens += approx
            retrieved.append(item)

        # 5. Log the query search metrics
        log_item = RetrievalLog(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            product_id=product_id,
            query_text=query,
            retrieved_chunks_json=json.dumps([
                {"id": x["id"], "score": x.get("combined_score", 0.0)}
                for x in retrieved
            ])
        )
        await self.logs_repo.create(log_item)
        await self.logs_repo.db.commit()

        return retrieved[:limit]
