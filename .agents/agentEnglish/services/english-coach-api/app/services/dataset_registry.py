import os
import uuid
import json
from typing import Optional, List
from sqlalchemy import select, update
from app.db.models import Dataset, KnowledgeDocument, KnowledgeChunk
from app.repositories.datasets import DatasetsRepository
from app.repositories.knowledge_documents import KnowledgeDocumentsRepository
from app.repositories.knowledge_chunks import KnowledgeChunksRepository
from app.data_ingestion.pipeline import IngestionPipeline
from app.data_ingestion.chunking import ParagraphChunker
from app.services.embedding_service import EmbeddingService

class DatasetRegistryService:
    """Manages datasets configurations and executes document chunk ingestion workflows."""

    def __init__(
        self,
        datasets_repo: DatasetsRepository,
        doc_repo: KnowledgeDocumentsRepository,
        chunk_repo: KnowledgeChunksRepository,
        embedding_service: EmbeddingService
    ):
        self.datasets_repo = datasets_repo
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.embedding_service = embedding_service
        self.pipeline = IngestionPipeline()

    async def register_dataset(
        self,
        tenant_id: str,
        product_id: str,
        name: str,
        version: str,
        file_path: str
    ) -> Dataset:
        """Registers a pending dataset version record in database catalog."""
        dataset = Dataset(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            product_id=product_id,
            name=name,
            version=version,
            file_path=file_path,
            status="PENDING"
        )
        await self.datasets_repo.create(dataset)
        await self.datasets_repo.db.commit()
        return dataset

    async def ingest_dataset(self, dataset_id: str) -> None:
        """Loads file documents, segments text, constructs metadata, and generates embeddings."""
        dataset = await self.datasets_repo.get_by_id(dataset_id)
        if not dataset:
            raise ValueError("Dataset not found")

        dataset.status = "INGESTING"
        await self.datasets_repo.db.commit()

        try:
            # 1. Extract documents using normalizers pipeline
            raw_docs = self.pipeline.process_file(dataset.file_path)
            
            # 2. Add document metadata records
            for idx_doc, doc_item in enumerate(raw_docs):
                doc_id = f"doc-{dataset_id}-{idx_doc}"
                k_doc = KnowledgeDocument(
                    id=doc_id,
                    tenant_id=dataset.tenant_id,
                    product_id=dataset.product_id,
                    name=os.path.basename(dataset.file_path),
                    source_type=os.path.splitext(dataset.file_path)[1].replace(".", ""),
                    metadata_json=json.dumps(doc_item.get("metadata", {}))
                )
                await self.doc_repo.create(k_doc)
                
                # 3. Create overlapping chunk splits
                chunks = ParagraphChunker.split_into_chunks(doc_item.get("content", ""))
                for idx_chunk, chunk_item in enumerate(chunks):
                    content = chunk_item.get("content", "")
                    # Generate semantic search embedding
                    vector = await self.embedding_service.get_embedding(content)
                    
                    k_chunk = KnowledgeChunk(
                        id=f"{doc_id}-chunk-{idx_chunk}",
                        doc_id=doc_id,
                        tenant_id=dataset.tenant_id,
                        product_id=dataset.product_id,
                        content=content,
                        embedding_json=json.dumps(vector),
                        metadata_json=json.dumps(doc_item.get("metadata", {}))
                    )
                    await self.chunk_repo.create(k_chunk)

            dataset.status = "INGESTED"
        except Exception as e:
            dataset.status = "ERROR"
            raise e
        finally:
            await self.datasets_repo.db.commit()
