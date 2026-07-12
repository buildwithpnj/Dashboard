# Platform Alerting and Incident Rules

This document describes metrics checking rules monitoring platform thresholds.

---

## 1. Alerting Metrics Thresholds

The API exposes `/v1/admin/alerts` to scan real-time metrics logs and active database records:

| Trigger ID | Checking Condition | Severity | Description |
| :--- | :--- | :--- | :--- |
| `AUTH_DENIAL_SPIKE` | Auth denials count > 10 | CRITICAL | Security alert indicating credential stuffing or token expiration. |
| `QUEUE_FAILURE_SPIKE` | Failed task runs > 5 | WARNING | Queue issue indicating workers are crashing or database locks are failing. |
| `ESCALATION_ANOMALY` | Active check-in escalations > 3 | CRITICAL | Safety alert indicating multiple elder distress checkins. |

---

## 2. Investigation Runbook

When an alert is active:
1. **Check System Config**: Hit `GET /v1/admin/system-summary` to confirm environment states.
2. **Scan Failed Tasks**: Hit `GET /v1/admin/task-runs` to locate task error traceback details.
3. **Trace Safety Escalations**: Hit `GET /v1/admin/escalations` to fetch parent profiles in distress state.
