import os
import tempfile
import pytest
from app.data_ingestion.pipeline import IngestionPipeline

def test_ingestion_pipeline_md_and_jsonl():
    pipeline = IngestionPipeline()
    
    # 1. Test markdown parser and whitespace normalizer
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False, encoding="utf-8") as f:
        f.write("Line 1.  \n\n\n  Line 2.  \n\n  Line 2.  ")
        md_name = f.name
        
    try:
        docs = pipeline.process_file(md_name)
        assert len(docs) == 1
        # Whitespace normalised (no multi-newline, no double space)
        assert docs[0]["content"] == "Line 1. \n\n Line 2. \n\n Line 2."
    finally:
        os.remove(md_name)

    # 2. Test JSONL parser and content deduplicator
    with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w", delete=False, encoding="utf-8") as f:
        f.write('{"text": "A simple sentence."}\n')
        f.write('{"text": "A simple sentence."}\n') # Duplicate content
        f.write('{"text": "Another different sentence."}\n')
        jsonl_name = f.name
        
    try:
        docs = pipeline.process_file(jsonl_name)
        # 1 duplicate filtered out -> only 2 records remain
        assert len(docs) == 2
        assert docs[0]["content"] == "A simple sentence."
        assert docs[1]["content"] == "Another different sentence."
    finally:
        os.remove(jsonl_name)
