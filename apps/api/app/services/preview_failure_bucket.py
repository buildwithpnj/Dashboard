from .preview_quality_monitor import PreviewQualityMonitor
from typing import Dict, List, Any

class PreviewFailureBucket:
    @classmethod
    def get_bucketed_failures(cls) -> Dict[str, List[Dict[str, Any]]]:
        failures = PreviewQualityMonitor.get_failures()
        buckets: Dict[str, List[Dict[str, Any]]] = {
            "unsafe_words": [],
            "repetition": [],
            "excessive_length": [],
            "general_low_quality": []
        }
        
        for f in failures:
            res_lower = f["response"].lower()
            if len(f["response"]) > 1200:
                buckets["excessive_length"].append(f)
            elif any(w in res_lower for w in ["system prompt", "openai", "apikey"]):
                buckets["unsafe_words"].append(f)
            else:
                buckets["general_low_quality"].append(f)
                
        return buckets
