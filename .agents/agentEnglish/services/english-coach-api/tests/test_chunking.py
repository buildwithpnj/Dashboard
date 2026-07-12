from app.data_ingestion.chunking import ParagraphChunker

def test_paragraph_chunker_splitting():
    text = "First paragraph content details.\n\nSecond paragraph content information."
    
    # Split paragraphs with small token size (preserves paragraphs intact)
    chunks = ParagraphChunker.split_into_chunks(text, max_tokens=5, overlap=0)
    assert len(chunks) == 2
    assert chunks[0]["content"] == "First paragraph content details."
    assert chunks[1]["content"] == "Second paragraph content information."

    # Giant paragraph exceeding limit gets subdivided
    giant_text = " ".join(["word"] * 30)
    chunks = ParagraphChunker.split_into_chunks(giant_text, max_tokens=15, overlap=5)
    assert len(chunks) > 1
    # Check overlap items
    assert "word" in chunks[1]["content"]
