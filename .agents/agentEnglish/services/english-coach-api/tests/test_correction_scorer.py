from app.services.scoring.correction_scorer import CorrectionScorer

def test_correction_scorer():
    scorer = CorrectionScorer()

    # Perfect match
    scores = scorer.score(
        input_text="He go to school.",
        model_output="He went to school.",
        reference_corrections=["He went to school."]
    )
    assert scores["meaning_preservation"] == 1.0
    assert scores["grammar_quality"] == 1.0
    assert scores["brevity_control"] == 1.0

    # No correction made
    scores_no_change = scorer.score(
        input_text="He go to school.",
        model_output="He go to school.",
        reference_corrections=["He went to school."]
    )
    assert scores_no_change["grammar_quality"] == 0.3
