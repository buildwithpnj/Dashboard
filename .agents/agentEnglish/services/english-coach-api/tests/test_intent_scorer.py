from app.services.scoring.intent_scorer import IntentScorer

def test_intent_scorer():
    scorer = IntentScorer()

    # Perfect intent match
    scores = scorer.score(
        utterance="set alarm",
        predicted_intent="alarm_set",
        reference_intent="alarm_set",
        predicted_slots="[time: 5am]",
        reference_slots="[time: 5am]"
    )
    assert scores["intent_accuracy"] == 1.0
    assert scores["slot_extraction_quality"] == 1.0
    assert scores["routing_correctness"] == 1.0

    # Partial intent match
    scores_partial = scorer.score(
        utterance="set alarm",
        predicted_intent="alarm",
        reference_intent="alarm_set"
    )
    assert scores_partial["intent_accuracy"] == 0.5
    assert scores_partial["routing_correctness"] == 0.5
