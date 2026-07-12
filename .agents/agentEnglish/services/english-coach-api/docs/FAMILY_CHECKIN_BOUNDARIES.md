# Family Check-in Boundaries & Safety Policies

The Family Check-in agent is designed to verify the safety and daily comfort of elderly parents (such as Prakash's mom). It maintains strict safety and health boundaries.

---

## 1. Safety Policies & Distress Flagging

The Family Check-in pipeline operates with a **Fail-Safe Alert System**:

- **Distress Keyword Triggers**: Incoming parent messages are actively parsed for distress indicators, injuries, or emergencies.
- **Trigger Words**: Keywords include:
  - *Hindi*: `gira`, `giri` (fell), `dard` (pain), `chhot` (injury), `hospital`, `emergency`, `khun` (blood), `marna` (die).
  - *English*: `chest`, `pain`, `hurt`, `fell`, `accident`, `emergency`, `ambulance`.
- **Escalation Ingestion**: If any trigger word matches:
  - The status is immediately updated to `escalated` and saved to `checkin_runs`.
  - An email/SMS alert trigger log is emitted.
  - The API response body sets `escalation_triggered=true` and returns the complete active contact list (`escalation_contacts`) so the child can be notified immediately.

---

## 2. Wellness Limits & Medical Disclaimers

To protect user safety, the agent complies with the following boundaries:

- **No Medical Claims**: The agent *never* suggests diagnoses, prescribes medications, or comments on symptoms.
- **Warning Injection**: If the user shares symptom updates, a strict disclaimer is prepended to the feedback comments:
  - *"DISCLAIMER: This is a wellness check-in, not a medical diagnosis. Please consult a qualified doctor for any medical symptoms."*
- **Escalation Priority**: If the system detects medical updates, it guides the parent to contact their physician or emergency services immediately rather than attempting to answer.
