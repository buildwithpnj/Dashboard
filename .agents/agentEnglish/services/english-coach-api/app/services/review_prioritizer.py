from typing import List

class ReviewPrioritizer:
    """Service to prioritize the human-in-the-loop review backlog based on risk and learning value."""

    def prioritize(self, backlog: List[dict]) -> List[dict]:
        """Calculates a priority score for each backlog item and returns the list sorted descending."""
        scored_backlog = []
        for item in backlog:
            item_copy = item.copy()
            score = 1.0

            # 1. Composite score in [0.4, 0.6] (highest confusion)
            c_score = item_copy.get("composite_score")
            if c_score is not None:
                try:
                    c_score_val = float(c_score)
                    if 0.4 <= c_score_val <= 0.6:
                        score += 2.0
                except (ValueError, TypeError):
                    pass

            # 2. Task type is 'correction' and meaning preservation < 0.4 (high semantic risk)
            task_type = item_copy.get("task_type")
            meaning_preservation = item_copy.get("meaning_preservation")
            if task_type == 'correction' and meaning_preservation is not None:
                try:
                    mp_val = float(meaning_preservation)
                    if mp_val < 0.4:
                        score += 1.5
                except (ValueError, TypeError):
                    pass

            # 3. Input contains wellness safety flags
            has_safety_flag = False

            # Check explicit flag fields in the item dict
            for flag_key in ["wellness_flag", "safety_flag", "flagged", "is_flagged", "safety_flags", "wellness_flags"]:
                flag_val = item_copy.get(flag_key)
                if flag_val is True or (isinstance(flag_val, (int, float)) and flag_val > 0):
                    has_safety_flag = True
                    break

            # Check the content of the 'input' key
            input_val = item_copy.get("input")
            if not has_safety_flag and input_val:
                if isinstance(input_val, str):
                    input_lower = input_val.lower()
                    if any(k in input_lower for k in ["self-harm", "suicide", "depress", "anxiety", "kill myself", "hurt myself", "end my life"]):
                        has_safety_flag = True
                elif isinstance(input_val, dict):
                    if (
                        input_val.get("wellness_flag") is True
                        or input_val.get("safety_flag") is True
                        or input_val.get("flagged") is True
                    ):
                        has_safety_flag = True

            # Check the content of the 'input_text' key as fallback
            input_text = item_copy.get("input_text")
            if not has_safety_flag and isinstance(input_text, str):
                input_text_lower = input_text.lower()
                if any(k in input_text_lower for k in ["self-harm", "suicide", "depress", "anxiety", "kill myself", "hurt myself", "end my life"]):
                    has_safety_flag = True

            if has_safety_flag:
                score += 3.0

            item_copy["priority_score"] = score
            scored_backlog.append(item_copy)

        # Sort descending by priority_score
        scored_backlog.sort(key=lambda x: x["priority_score"], reverse=True)
        return scored_backlog
