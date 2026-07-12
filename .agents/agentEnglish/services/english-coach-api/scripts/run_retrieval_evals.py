import os
import json
import asyncio
from app.db.session import AsyncSessionLocal
from app.repositories.knowledge_chunks import KnowledgeChunksRepository
from app.repositories.retrieval_logs import RetrievalLogsRepository
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import HybridRetrievalService
from app.services.retrieval_eval_service import RetrievalEvalService

async def main():
    db = AsyncSessionLocal()
    chunks_repo = KnowledgeChunksRepository(db)
    logs_repo = RetrievalLogsRepository(db)
    emb_service = EmbeddingService()
    
    retrieval_service = HybridRetrievalService(chunks_repo, logs_repo, emb_service)
    
    dataset_path = "data/evals/retrieval/retrieval_dataset.jsonl"
    if not os.path.exists(dataset_path):
        print(f"Dataset path not found: {dataset_path}")
        return

    results = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            query = item["query"]
            gt = item["ground_truth_terms"]
            
            # Query hybrid context
            chunks = await retrieval_service.retrieve(
                tenant_id="default_tenant",
                product_id="english_coach",
                query=query,
                limit=3
            )
            
            metrics = RetrievalEvalService.evaluate(chunks, gt)
            results.append({
                "query": query,
                "metrics": metrics
            })
            
    out_path = "data/evals/retrieval/retrieval_results.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"Evaluated {len(results)} items. Results saved to {out_path}.")
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
