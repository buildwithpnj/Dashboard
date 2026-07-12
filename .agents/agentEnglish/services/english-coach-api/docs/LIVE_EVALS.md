# Live Evaluation Lane

This document describes the validation engine testing accuracy thresholds across English Coach, LifeOS, and Family Check-in golden datasets.

---

## 1. Evaluation Modes

The evaluation runner (`scripts/run_live_evals.py`) determines LLM completion scoring behavior using `settings.EVAL_MODE`:

- `mock`: Runs offline deterministic keyword checks against pre-cached mock responses (ideal for CI/CD checks).
- `local`: Custom local LLM providers.
- `live_openai`: Connects to live OpenAI APIs to check response alignments.

---

## 2. Golden Datasets

Golden test records are defined inside the `data/evals/` folder:
- `translation_eval.jsonl`, `correction_eval.jsonl`, `rewrite_eval.jsonl`, `ambiguity_eval.jsonl` (English Coach).
- `lifeos_eval.jsonl` (Sleep, exercise, calorie habits).
- `family_checkin_eval.jsonl` (Distress indicators and safe Hindi checkins).

---

## 3. Running Evaluators

Trigger the nightly evaluation suite using:
```bash
# Run evaluations
$env:PYTHONPATH="."; .venv\Scripts\python scripts/run_live_evals.py

# Print visual table summaries
$env:PYTHONPATH="."; .venv\Scripts\python scripts/report_live_evals.py
```

Runs complete successfully if the average score passes the target pass threshold (Default: `80%`).
