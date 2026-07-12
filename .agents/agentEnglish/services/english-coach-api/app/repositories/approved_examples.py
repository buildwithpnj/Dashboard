import json
import datetime
from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseFileRepository
from app.db.models import ApprovedExample as DBApprovedExample
from app.schemas.evals import ApprovedExample as SchemaApprovedExample

class ApprovedExamplesRepository:
    """Dual-mode repository saving examples to DB schemas or falling back to local JSONL files."""

    def __init__(self, db_session=None, filepath: Optional[str] = None):
        self.db_session = db_session
        self.file_repo = None
        if filepath:
            self.file_repo = BaseFileRepository(filepath)

    async def add_example(self, example: SchemaApprovedExample) -> None:
        """Saves a verified example translation. Writes to DB if active, also appends to JSONL."""
        if self.db_session:
            # Parse created_at safely
            created_at_dt = datetime.datetime.utcnow()
            if example.created_at:
                try:
                    cleaned_ts = example.created_at.replace("Z", "")
                    if "." in cleaned_ts:
                        created_at_dt = datetime.datetime.strptime(cleaned_ts, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        created_at_dt = datetime.datetime.strptime(cleaned_ts, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    pass
            
            db_ex = DBApprovedExample(
                id=example.id,
                product_id=example.tags[0] if example.tags else "english_coach",
                input_text=example.input_text,
                natural_english=example.natural_english,
                professional_english=example.professional_english,
                tags_json=json.dumps(example.tags),
                created_at=created_at_dt
            )
            self.db_session.add(db_ex)
            await self.db_session.flush()

        if self.file_repo:
            self.file_repo._append_line(example.model_dump())

    async def get_all(self, product_id: Optional[str] = None) -> List[SchemaApprovedExample]:
        """Loads and returns all approved examples from the active persistence mode."""
        if self.db_session:
            stmt = select(DBApprovedExample)
            if product_id:
                stmt = stmt.filter(DBApprovedExample.product_id == product_id)
            res = await self.db_session.execute(stmt)
            items = res.scalars().all()
            
            results = []
            for item in items:
                try:
                    tags = json.loads(item.tags_json)
                except Exception:
                    tags = [item.product_id]
                results.append(
                    SchemaApprovedExample(
                        id=item.id,
                        input_text=item.input_text,
                        natural_english=item.natural_english,
                        professional_english=item.professional_english,
                        tags=tags,
                        created_at=item.created_at.isoformat() + "Z"
                    )
                )
            return results

        if self.file_repo:
            lines = self.file_repo._read_lines()
            schema_list = [SchemaApprovedExample(**line) for line in lines]
            if product_id:
                schema_list = [
                    ex for ex in schema_list
                    if product_id in ex.tags or 
                       (product_id == "english_coach" and any(t in ex.tags for t in ["translation", "correction", "rewrite", "hinglish", "mixed"]))
                ]
            return schema_list
            
        return []

    async def get_all_sync(self, product_id: Optional[str] = None) -> List[SchemaApprovedExample]:
        """Synchronous fallback helper wrapper (loads from file directly)."""
        if self.file_repo:
            lines = self.file_repo._read_lines()
            schema_list = [SchemaApprovedExample(**line) for line in lines]
            if product_id:
                schema_list = [
                    ex for ex in schema_list
                    if product_id in ex.tags or 
                       (product_id == "english_coach" and any(t in ex.tags for t in ["translation", "correction", "rewrite", "hinglish", "mixed"]))
                ]
            return schema_list
        return []

    def _overwrite_all(self, records: List[dict]) -> None:
        """Helper forwarder method for legacy test files cleanup."""
        if self.file_repo:
            self.file_repo._overwrite_all(records)
