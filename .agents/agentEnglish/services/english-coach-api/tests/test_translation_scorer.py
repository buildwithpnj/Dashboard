from app.services.scoring.translation_scorer import TranslationScorer

def test_translation_scorer():
    scorer = TranslationScorer()

    # Perfect translation
    scores = scorer.score(
        source_text="नमस्ते",
        model_output="Hello",
        reference_text="Hello",
        source_lang="hi",
        target_lang="en"
    )
    assert scores["semantic_preservation"] == 1.0
    assert scores["naturalness"] == 1.0
    assert scores["script_handling"] == 1.0
    assert scores["hinglish_ambiguity"] == 1.0

    # Script mixing detection (Devanagari characters left in output)
    scores_mixed = scorer.score(
        source_text="नमस्ते",
        model_output="Hello नमस्ते",
        reference_text="Hello",
        source_lang="hi",
        target_lang="en"
    )
    assert scores_mixed["naturalness"] < 0.5
    assert scores_mixed["script_handling"] <= 0.5

