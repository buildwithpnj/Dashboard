from app.celery_app import celery_app


@celery_app.task
def process_staging_entry(entry_id: str):
    """Placeholder task for staging entry ingestion (structured JSON extraction)."""
    print(f"[Celery] Processing staging entry: {entry_id}")
    return {"status": "success", "processed_id": entry_id}


@celery_app.task
def generate_note_embeddings(note_id: str):
    """Placeholder task for generating note vectors via pgvector."""
    print(f"[Celery] Generating embeddings for note: {note_id}")
    return {"status": "success", "note_id": note_id}
