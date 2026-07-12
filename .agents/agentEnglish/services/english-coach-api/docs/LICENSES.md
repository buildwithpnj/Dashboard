# Dataset Licenses & Non-Commercial Compliance

This document outlines the licensing details, provenance records, and non-commercial restrictions for the benchmark datasets integrated into the Warborn Multi-Agent Platform Core.

---

## 1. Benchmark Datasets Compliance Table

| Dataset | Publisher / Source | License | Commercial Use | Restriction Flag | Compliance Details |
|---------|---------------------|---------|----------------|------------------|---------------------|
| **JFLEG** | Johns Hopkins University | CC BY-NC-SA 4.0 | **NO** | `commercial_restriction=True` | Restricted to non-commercial evaluation and research only. |
| **Samanantar** | AI4Bharat | CC BY 4.0 | **NO** | `commercial_restriction=True` | Primary papers explicitly state research-only distribution restrictions. |
| **MASSIVE** | Amazon Alexa AI | CC BY 4.0 | **YES** | `commercial_restriction=False` | Openly usable for commercial intent routing checks. |

---

## 2. Ingestion-Gate Compliance Policy

To prevent intellectual property leaks or license violations, the platform implements an automated safety gate inside `LicenseChecker`:

- **Development/Testing**: Ingestion is permitted, but the console emits a warning highlighting the dataset license terms and commercial restrictions.
- **Production**: If `APP_ENV=production`, any ingestion command or dataset manifest matching `commercial_restriction=True` is **blocked and rejected automatically** to preserve strict production safety.
