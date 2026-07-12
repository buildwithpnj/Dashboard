from app.services.retrieval_eval_service import RetrievalEvalService

def test_retrieval_evals_computations():
    # Chunks returned by search
    retrieved = [
        {"content": "A simple sentence about network problems."},
        {"content": "Details on sleep habits logged."}
    ]
    
    # 1. Matches first rank (mrr = 1.0, hit = 1.0)
    m1 = RetrievalEvalService.evaluate(retrieved, ["network"])
    assert m1["hit_at_k"] == 1.0
    assert m1["mrr"] == 1.0
    assert m1["precision"] == 0.5

    # 2. Matches second rank (mrr = 0.5, hit = 1.0)
    m2 = RetrievalEvalService.evaluate(retrieved, ["sleep"])
    assert m2["hit_at_k"] == 1.0
    assert m2["mrr"] == 0.5
    assert m2["precision"] == 0.5

    # 3. No matches (mrr = 0.0, hit = 0.0)
    m3 = RetrievalEvalService.evaluate(retrieved, ["unknown"])
    assert m3["hit_at_k"] == 0.0
    assert m3["mrr"] == 0.0
    assert m3["precision"] == 0.0
