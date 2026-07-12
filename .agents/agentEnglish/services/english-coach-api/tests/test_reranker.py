from app.services.reranker import SimpleReranker

def test_reranker_sorting_by_lexical_overlap():
    candidates = [
        {"id": "chunk-1", "content": "A standard generic sentence containing nothing.", "similarity": 0.9},
        {"id": "chunk-2", "content": "Prakash had network connectivity problems during session calls.", "similarity": 0.7}
    ]
    
    # query matches terms in chunk-2 (lexical terms: "network", "problems")
    query = "network connectivity problems"
    
    reranked = SimpleReranker.rerank(query, candidates)
    
    # Despite chunk-1 having higher raw similarity (0.9 vs 0.7), 
    # chunk-2 has higher lexical density match (3 matches), placing it first!
    assert reranked[0]["id"] == "chunk-2"
