from app.services.v8_eval_router import V8EvalRouter

def test_eval_router_scoring():
    router = V8EvalRouter()

    # 1. Correction scoring
    case_correction = {
        "task_type": "correction",
        "source_text": "He go to school.",
        "reference_corrections": ["He went to school."]
    }
    scores_correction = router.score_example(case_correction, "He went to school.")
    assert "meaning_preservation" in scores_correction
    assert scores_correction["meaning_preservation"] == 1.0

    # 2. Translation scoring
    case_translation = {
        "task_type": "translation",
        "source_text": "नमस्ते",
        "target_text": "Hello"
    }
    scores_translation = router.score_example(case_translation, "Hello")
    assert "semantic_preservation" in scores_translation
    assert scores_translation["semantic_preservation"] == 1.0

    # 3. Intent classification routing scoring
    case_intent = {
        "task_type": "intent_routing",
        "utterance": "set alarm for 5am",
        "intent": "alarm_set"
    }
    scores_intent = router.score_example(case_intent, "alarm_set")
    assert "intent_accuracy" in scores_intent
    assert scores_intent["intent_accuracy"] == 1.0
