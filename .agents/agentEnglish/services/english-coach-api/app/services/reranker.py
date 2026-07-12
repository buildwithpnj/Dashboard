from typing import List, Dict, Any

class SimpleReranker:
    """Sorts semantic candidates using lexical word overlaps to optimize relevance ranking."""

    @staticmethod
    def rerank(query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Computes combined score mixing semantic similarity and keyword density weights."""
        if not query:
            return candidates

        q_terms = set(query.lower().split(" "))
        scored_candidates = []
        
        for item in candidates:
            text = item.get("content", "").lower()
            # Count target query terms matching chunk text
            matched = sum(1 for term in q_terms if term in text)
            lexical_ratio = matched / max(1, len(q_terms))
            
            similarity = item.get("similarity", 0.0)
            combined = (similarity * 0.7) + (lexical_ratio * 0.3)
            
            res = dict(item)
            res["combined_score"] = combined
            scored_candidates.append(res)
            
        scored_candidates.sort(key=lambda x: x["combined_score"], reverse=True)
        return scored_candidates
