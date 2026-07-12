from typing import Dict, Any, List
from app.repositories.preview_events import PreviewEventsRepository
from app.services.preview_budget_service import PreviewBudgetService

class PreviewCostTuner:
    @classmethod
    def get_efficiency_report(cls) -> Dict[str, Any]:
        events = PreviewEventsRepository.get_all_events()
        total_runs = len(events)
        
        # Calculate prompt class breakdown: average tokens and cost
        class_costs: Dict[str, List[float]] = {}
        class_tokens: Dict[str, List[int]] = {}
        
        for e in events:
            # Classify prompt lightly by length or keywords
            p_len = len(e["prompt"])
            p_class = "short" if p_len < 20 else ("medium" if p_len < 100 else "long")
            
            class_costs.setdefault(p_class, []).append(e["cost"])
            class_tokens.setdefault(p_class, []).append(e["tokens"])
            
        report: Dict[str, Any] = {}
        for p_class in ["short", "medium", "long"]:
            costs = class_costs.get(p_class, [])
            tokens = class_tokens.get(p_class, [])
            
            report[p_class] = {
                "count": len(costs),
                "avg_cost_usd": round(sum(costs) / len(costs), 6) if costs else 0.0,
                "avg_tokens": round(sum(tokens) / len(tokens), 1) if tokens else 0.0
            }
            
        return report
