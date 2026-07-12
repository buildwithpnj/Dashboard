from typing import List, Dict, Any

class ParagraphChunker:
    """Chunks text into paragraph-preserving blocks with token budget limits."""

    @staticmethod
    def split_into_chunks(text: str, max_tokens: int = 200, overlap: int = 50) -> List[Dict[str, Any]]:
        """Splits content into segments preserving context overlap bounds."""
        if not text.strip():
            return []

        paragraphs = text.split("\n\n")
        chunks = []
        current_words = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_words = para.split(" ")
            
            # If paragraph overflows size limit, save current chunk
            if len(current_words) + len(para_words) > max_tokens:
                if current_words:
                    chunks.append(" ".join(current_words))
                    # Keep overlap from the end of the previous chunk
                    if overlap > 0:
                        current_words = current_words[-overlap:] if len(current_words) > overlap else current_words
                    else:
                        current_words = []
                
                # Handle single giant paragraph case by subdividing it
                if len(para_words) > max_tokens:
                    for i in range(0, len(para_words), max_tokens - overlap):
                        part = para_words[i:i + max_tokens]
                        if part:
                            chunks.append(" ".join(part))
                    current_words = []
                else:
                    current_words.extend(para_words)
            else:
                current_words.extend(para_words)
                
        if current_words:
            chunks.append(" ".join(current_words))
            
        return [
            {
                "content": chunk,
                "approx_tokens": len(chunk.split(" "))
            }
            for chunk in chunks
        ]
