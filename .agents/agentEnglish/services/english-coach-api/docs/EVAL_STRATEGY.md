# Evaluation Strategy & Accuracy Metric Harness

This document describes the offline validation framework, scoring dimensions, and regression testing strategy for the Warborn Agent Platform Core.

---

## 1. 6-Dimension Scoring Index

Every coaching transaction is scored on a `0.0` to `1.0` index across 6 dimensions:

1. **Meaning Preservation** (25% weight): Computes set-based Jaccard similarity word overlaps between coached translation strings and reference targets.
2. **Grammar Accuracy** (20% weight): Verifies subject-verb alignments and correct preposition/article usage.
3. **Naturalness** (15% weight): Rates vocabulary flow to ensure the output sounds natural.
4. **Tone Match** (15% weight): Verifies correct formal/informal styles mapping matching target intents.
5. **Ambiguity Handling** (15% weight): Checks that incomplete prompts trigger ambiguity states (`ambiguity=True`) and return exactly one clarification question.
6. **Explanation Quality** (10% weight): Verifies that explanations are constructive and concise (between 5 and 40 words).

---

## 2. Token Size Budgets & Prefix Caching

- **Stable Prefix Instruction Placement**: Static system instructions and schema layouts are placed at the beginning of the prompt to maximize API prefix caching hits.
- **Dynamic Context Budget Limits**: The `MemoryService` dynamically recalls approved correction pairs. If total tokens exceed `MAX_DYNAMIC_CONTEXT_TOKENS` (500 tokens), the `enforce_context_budget` utility drops exemplars and clips the profile summary to protect stable instructions cache keys. Truncations are logged automatically.

---

## 3. Accuracy Regression Verification

- **Evaluation Datasets**: Local datasets are stored under `data/evals/` containing test cases:
  - `translation_eval.jsonl` (translation targets)
  - `correction_eval.jsonl` (broken English targets)
  - `rewrite_eval.jsonl` (tone rewriting targets)
  - `ambiguity_eval.jsonl` (ambiguous input targets)
- **Run Execution**: Running `python scripts/run_evals.py` executes the entire suite. If average weighted accuracy falls below the `80%` threshold, the script returns exit code `1` to prevent buggy deployments.
- **Unicode terminal support**: Running `python scripts/generate_eval_report.py` reconfigures terminal stdout to print correct charts including Hindi Devnagari characters.

---

## 4. V8 Large-Scale Dataset Testing & Promotion Loop

V8 expands accuracy regression checks to support streaming large datasets (up to 1,000 examples per run) with tiered model routing, budget enforcement, and a quality-gated gold-data promotion loop.

### External Benchmark Datasets & License constraints

| Dataset | Source URL | Split | License | Intended Use | Commercial Restrictions |
|---------|------------|-------|---------|--------------|-------------------------|
| **JFLEG** | [HuggingFace - jfleg](https://huggingface.co/datasets/jhu-clsp/jfleg) | `test` | CC BY-NC-SA 4.0 | Grammar error correction evaluation | **YES** (Non-commercial only) |
| **Samanantar** | [HuggingFace - samanantar](https://huggingface.co/datasets/ai4bharat/samanantar) | `train` (`hi-en`) | CC BY 4.0 | Hindi-English parallel translation | **YES** (Research-use restrictions) |
| **MASSIVE** | [HuggingFace - MASSIVE](https://huggingface.co/datasets/qanastek/MASSIVE) | `test` | CC BY 4.0 | Intent routing classification | **NO** |

> [!WARNING]
> Licensing constraints are strictly validated by `LicenseChecker`. Datasets marked with `commercial_restriction=True` (JFLEG and Samanantar) are permitted only in development and testing environments, and will be blocked outright if run in `production`.

### Tiered Model Routing Strategy
To optimize token spend, examples are routed dynamically:
1. **Easy** (e.g. short utterances under 50 chars): Routed to the cheap model (`gpt-3.5-turbo`).
2. **Medium**: Routed to the standard model (`gpt-4o-mini`).
3. **Hard** (e.g. text > 200 chars or script mixing): Routed to the premium model (`gpt-4o`), capped at 5% of total run count.

### Budget & Stop Rules
Evaluations enforce a run-specific budget cap (default `$5.00`):
- **80% Utilization**: Automatically triggers a tier downgrade warning, routing remaining items to the cheap model.
- **100% Utilization**: Hard stops execution, saving progress to a JSON checkpoint so the run can be resumed later.

### Gold Dataset Promotion Policy
Only model outputs matching the following criteria are eligible for promotion:
- Composite score $\ge 0.85$.
- Clean provenance metadata logged (run ID, example hash, original source).
- Outputs are saved as `GoldExample` in `PENDING` review status. Operator approval in the admin operations dashboard promotes them to production-injectable gold dataset splits, while failures below `0.40` are archived as `HardNegativeExample` training pairs.

### CLI Operations

```bash
# 1. Execute a capped 1000-example run (e.g., JFLEG grammar checks)
$env:PYTHONPATH="."; .venv\Scripts\python scripts/run_large_evals.py --dataset jfleg --max-examples 1000 --max-budget 5.0

# 2. Print visual metrics summary run report
$env:PYTHONPATH="."; .venv\Scripts\python scripts/report_large_evals.py

# 3. Promote approved high-quality outputs to gold and hard-negatives
$env:PYTHONPATH="."; .venv\Scripts\python scripts/promote_gold_examples.py --threshold 0.85
```

