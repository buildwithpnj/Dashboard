import json
from typing import List, Dict, Any
from sqlalchemy import select, text
from app.repositories.base import BaseDBRepository
from app.db.models import KnowledgeChunk

class KnowledgeChunksRepository(BaseDBRepository[KnowledgeChunk]):
    """DB-backed repository managing text chunks, with production pgvector support and SQLite fallback."""

    def __init__(self, db):
        super().__init__(db, KnowledgeChunk)

    async def search_similar_chunks(
        self,
        tenant_id: str,
        product_id: str,
        query_embedding: List[float],
        limit: int = 5,
        threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Queries semantically similar chunks restricted to caller's tenant-scoping context."""
        dialect = self.db.bind.dialect.name
        
        if dialect == "postgresql":
            # Native pgvector similarity operator
            sql = text(
                "SELECT id, content, metadata_json, 1 - (embedding <=> :embedding_val) as similarity "
                "FROM knowledge_chunks "
                "WHERE tenant_id = :tenant_id AND product_id = :product_id "
                "AND 1 - (embedding <=> :embedding_val) >= :threshold "
                "ORDER BY embedding <=> :embedding_val ASC "
                "LIMIT :limit"
            )
            res = await self.db.execute(sql, {
                "tenant_id": tenant_id,
                "product_id": product_id,
                "embedding_val": str(query_embedding),
                "threshold": threshold,
                "limit": limit
            })
            return [
                {
                    "id": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]) if isinstance(row[2], str) else row[2],
                    "similarity": float(row[3])
                }
                for row in res.fetchall()
            ]
            
        # SQLite dialect local python similarity evaluation
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id
        )
        res = await self.db.execute(stmt)
        chunks = res.scalars().all()
        
        matches = []
        for chunk in chunks:
            try:
                emb = json.loads(chunk.embedding_json)
                if not isinstance(emb, list):
                    continue
                # Calculate cosine similarity
                dot = sum(x * y for x, y in zip(query_embedding, emb))
                mag1 = sum(x * x for x in query_embedding) ** 0.5
                mag2 = sum(x * x for x in emb) ** 0.5
                sim = dot / (mag1 * mag2) if (mag1 * mag2) > 0 else 0.0
                
                if sim >= threshold:
                    matches.append({
                        "id": chunk.id,
                        "content": chunk.content,
                        "metadata": json.loads(chunk.metadata_json) if chunk.metadata_json else {},
                        "similarity": sim
                    })
            except Exception:
                continue
                
        # Sort desc and apply limit
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches[:limit]
