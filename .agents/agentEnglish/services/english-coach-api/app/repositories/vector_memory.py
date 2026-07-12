import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class VectorMemoryRepository:
    """Production-ready pgvector similarity search repository with SQLite compatibility fallback."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_vector(self, record_id: str, text_content: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        """Appends a vector embedding item to database storage."""
        dialect = self.db.bind.dialect.name
        if dialect == "postgresql":
            # Execute pgvector raw INSERT
            sql = text(
                "INSERT INTO vector_memories (id, content, embedding, metadata_json) "
                "VALUES (:id, :content, :embedding, :metadata_json)"
            )
            await self.db.execute(sql, {
                "id": record_id,
                "content": text_content,
                "embedding": str(embedding), # pgvector parses list strings directly
                "metadata_json": json.dumps(metadata)
            })
        else:
            logger.info("Local SQLite dialect active: skipping pgvector insert command.")

    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 3,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Performs cosine distance similarity queries on postgres, returning stubs on local SQLite."""
        dialect = self.db.bind.dialect.name
        if dialect == "postgresql":
            # pgvector distance operator <=> maps to cosine distance (1 - cosine_distance = cosine_similarity)
            sql = text(
                "SELECT id, content, metadata_json, 1 - (embedding <=> :embedding_val) as similarity "
                "FROM vector_memories "
                "WHERE 1 - (embedding <=> :embedding_val) >= :threshold "
                "ORDER BY embedding <=> :embedding_val ASC "
                "LIMIT :limit"
            )
            res = await self.db.execute(sql, {
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
            
        logger.info("Local SQLite dialect active: skipping pgvector search query.")
        return []
