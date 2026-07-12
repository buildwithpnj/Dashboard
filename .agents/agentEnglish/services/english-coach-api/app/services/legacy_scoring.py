from typing import Dict, Any, Optional
from app.schemas.evals import EvalCase
from app.schemas.coach import CoachRespondResponse

def calculate_jaccard_similarity(s1: str, s2: str) -> float:
    """Calculates Jaccard word set similarity between two text strings."""
    if not s1 or not s2:
        return 0.0
    w1 = {w.strip(".,?!;:()\"'") for w in s1.lower().split() if w.strip()}
    w2 = {w.strip(".,?!;:()\"'") for w in s2.lower().split() if w.strip()}
    if not w1 and not w2:
        return 1.0
    intersection = w1.intersection(w2)
    union = w1.union(w2)
    return len(intersection) / len(union)

class ScoringEngine:
    """Calculates scores for coached responses against reference test cases."""

    # Metric dimension weights summing to 1.0
    WEIGHTS = {
        "meaning_preservation": 0.25,
        "grammar_accuracy": 0.20,
        "naturalness": 0.15,
        "tone_match": 0.15,
        "explanation_quality": 0.10,
        "ambiguity_handling": 0.15
    }

    def score_response(self, case: EvalCase, response: CoachRespondResponse) -> Dict[str, float]:
        """Scores a single coach response across six linguistic dimensions.
        
        Returns:
            Dictionary containing dimension scores (0.0 to 1.0).
        """
        scores = {}
        
        # 1. Ambiguity Handling
        if case.expected_ambiguity:
            # Coached response must flag ambiguity and output a question
            if response.ambiguity and response.clarification_question:
                scores["ambiguity_handling"] = 1.0
            else:
                scores["ambiguity_handling"] = 0.0
        else:
            # Must NOT flag ambiguity
            if not response.ambiguity:
                scores["ambiguity_handling"] = 1.0
            else:
                scores["ambiguity_handling"] = 0.0

        # 2. Tone Match
        if response.intent == case.expected_intent:
            scores["tone_match"] = 1.0
        else:
            # Minor penalty if styles overlap
            scores["tone_match"] = 0.4

        # 3. Meaning Preservation
        if case.expected_ambiguity:
            # If ambiguous, natural and professional should be empty (None)
            if response.natural_english is None and response.professional_english is None:
                scores["meaning_preservation"] = 1.0
            else:
                scores["meaning_preservation"] = 0.0
        else:
            # Compare output sentences against reference sentences using Jaccard Similarity
            sim_natural = calculate_jaccard_similarity(response.natural_english, case.reference_natural)
            sim_prof = calculate_jaccard_similarity(response.professional_english, case.reference_professional)
            scores["meaning_preservation"] = (sim_natural + sim_prof) / 2.0

        # 4. Grammar Accuracy
        if case.expected_ambiguity:
            scores["grammar_accuracy"] = 1.0
        else:
            # Simple heuristic: Perfect similarity = perfect grammar.
            # Otherwise we rate grammar based on how close it matches the expected grammar.
            sim_natural = calculate_jaccard_similarity(response.natural_english, case.reference_natural)
            scores["grammar_accuracy"] = max(0.5, sim_natural)

        # 5. Naturalness
        if case.expected_ambiguity:
            scores["naturalness"] = 1.0
        else:
            sim_prof = calculate_jaccard_similarity(response.professional_english, case.reference_professional)
            scores["naturalness"] = max(0.5, sim_prof)

        # 6. Explanation Quality
        if case.expected_ambiguity:
            if response.explanation is None:
                scores["explanation_quality"] = 1.0
            else:
                scores["explanation_quality"] = 0.5
        else:
            explanation = response.explanation
            if not explanation:
                scores["explanation_quality"] = 0.0
            else:
                words = explanation.split()
                # Brief explanation check: 5 to 40 words is optimal
                if 5 <= len(words) <= 40:
                    scores["explanation_quality"] = 1.0
                elif len(words) > 40:
                    scores["explanation_quality"] = 0.7  # minor penalty for wordiness
                else:
                    scores["explanation_quality"] = 0.5  # minor penalty for too short
                    
        return scores

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Computes aggregate score based on predefined weights."""
        weighted = 0.0
        for dimension, weight in self.WEIGHTS.items():
            weighted += scores.get(dimension, 0.0) * weight
        return round(weighted, 4)
