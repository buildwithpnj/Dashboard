from typing import List
from app.db.models import LiveQualityMetric

class BaselineComparator:
    """Compares current rolling quality metrics against a historical baseline to identify performance regressions."""

    def compare(self, current: LiveQualityMetric, baseline: LiveQualityMetric) -> List[dict]:
        """
        Compares metrics between current and baseline.
        Returns list of dict alerts: 
        {"metric_name": str, "baseline": float, "current": float, "diff_pct": float, "triggered": bool, "severity": "warning"|"critical"}
        
        Metrics compared:
        - avg_score: triggers warning if drop >= 5% (0.05 absolute), critical if drop >= 10% (0.10 absolute)
        - escalation_rate: triggers warning if increase >= 2% (0.02 absolute)
        - budget_spend: triggers warning if increase >= 20%
        - pass_rate: triggers warning if drop >= 5%
        """
        alerts = []

        # 1. avg_score comparison (drop >= 0.05 is warning, >= 0.10 is critical)
        avg_score_drop = baseline.avg_score - current.avg_score
        avg_score_diff_pct = ((current.avg_score - baseline.avg_score) / baseline.avg_score * 100) if baseline.avg_score else 0.0
        avg_score_triggered = avg_score_drop >= 0.05
        avg_score_severity = "critical" if avg_score_drop >= 0.10 else "warning"
        alerts.append({
            "metric_name": "avg_score",
            "baseline": float(baseline.avg_score),
            "current": float(current.avg_score),
            "diff_pct": float(avg_score_diff_pct),
            "triggered": bool(avg_score_triggered),
            "severity": avg_score_severity
        })

        # 2. pass_rate comparison (drop >= 0.05 is warning)
        pass_rate_drop = baseline.pass_rate - current.pass_rate
        pass_rate_diff_pct = ((current.pass_rate - baseline.pass_rate) / baseline.pass_rate * 100) if baseline.pass_rate else 0.0
        pass_rate_triggered = pass_rate_drop >= 0.05
        alerts.append({
            "metric_name": "pass_rate",
            "baseline": float(baseline.pass_rate),
            "current": float(current.pass_rate),
            "diff_pct": float(pass_rate_diff_pct),
            "triggered": bool(pass_rate_triggered),
            "severity": "warning"
        })

        # 3. escalation_rate comparison (increase >= 0.02 is warning)
        escalation_increase = current.escalation_rate - baseline.escalation_rate
        escalation_diff_pct = ((current.escalation_rate - baseline.escalation_rate) / baseline.escalation_rate * 100) if baseline.escalation_rate else 0.0
        escalation_triggered = escalation_increase >= 0.02
        alerts.append({
            "metric_name": "escalation_rate",
            "baseline": float(baseline.escalation_rate),
            "current": float(current.escalation_rate),
            "diff_pct": float(escalation_diff_pct),
            "triggered": bool(escalation_triggered),
            "severity": "warning"
        })

        # 4. budget_spend comparison (increase >= 20% relative is warning)
        budget_increase_pct = ((current.budget_spend - baseline.budget_spend) / baseline.budget_spend) if baseline.budget_spend else 0.0
        budget_diff_pct = budget_increase_pct * 100
        budget_triggered = budget_increase_pct >= 0.20
        alerts.append({
            "metric_name": "budget_spend",
            "baseline": float(baseline.budget_spend),
            "current": float(current.budget_spend),
            "diff_pct": float(budget_diff_pct),
            "triggered": bool(budget_triggered),
            "severity": "warning"
        })

        return alerts
