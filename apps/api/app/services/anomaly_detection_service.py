import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.anomaly_incident import AnomalyIncident
from app.schemas.anomaly_signal_schema import AnomalySignalSchema
from typing import Dict, Any, List

class AnomalyDetectionService:
    @classmethod
    async def log_anomaly(
        cls,
        db: AsyncSession,
        req: AnomalySignalSchema
    ) -> AnomalyIncident:
        """
        Creates new anomaly occurrences logs.
        """
        incident = AnomalyIncident(
            id=str(uuid.uuid4()),
            tenant_id=req.tenant_id,
            signal_type=req.signal_type,
            severity=req.severity,
            incident_status="active",
            summary=req.summary
        )
        db.add(incident)
        await db.commit()
        return incident

    @classmethod
    def detect_loop_anomalies(
        cls,
        trace_history: List[str]
    ) -> Dict[str, Any]:
        """
        Scans trace history to detect loops or repeats.
        Returns anomaly report.
        """
        repeats = {}
        for trace in trace_history:
            repeats[trace] = repeats.get(trace, 0) + 1

        flagged = [t for t, count in repeats.items() if count > 2]
        return {
            "anomalies_detected": len(flagged) > 0,
            "flagged_repeats": flagged,
            "severity": "CRITICAL" if len(flagged) > 1 else "WARNING"
        }
