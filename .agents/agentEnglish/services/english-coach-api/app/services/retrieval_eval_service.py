from typing import List, Dict, Any

class RetrievalEvalService:
    """Calculates search accuracy metrics comparing retrieved content to target ground truth terms."""

    @staticmethod
    def evaluate(
        retrieved_chunks: List[Dict[str, Any]],
        ground_truth_terms: List[str]
    ) -> Dict[str, Any]:
        """Runs precision and recall evaluations on search chunks lists."""
        if not ground_truth_terms:
            return {"hit_at_k": 0.0, "mrr": 0.0, "precision": 0.0, "recall": 0.0}

        texts = [chunk.get("content", "").lower() for chunk in retrieved_chunks]
        
        hit = 0.0
        first_rank = 0
        hits_count = 0
        
        for term in ground_truth_terms:
            term_lower = term.lower()
            for idx, txt in enumerate(texts):
                if term_lower in txt:
                    hits_count += 1
                    hit = 1.0
                    if first_rank == 0:
                        first_rank = idx + 1
                    break

        mrr = 1.0 / first_rank if first_rank > 0 else 0.0
        precision = hits_count / len(retrieved_chunks) if retrieved_chunks else 0.0
        recall = hits_count / len(ground_truth_terms)

        return {
            "hit_at_k": hit,
            "mrr": mrr,
            "precision": precision,
            "recall": recall
        }
