# Review 2 Project Progress Report

## Project Title
Confidentiality-Aware Summarisation and Sharing Assistant Enforcing Access Boundaries

## Overview
This project is a software-based confidentiality-aware assistant for university environments. It enforces role-based access boundaries and prevents sensitive information from being exposed through document access, summarisation and sharing workflows.

## Work Completed
Implemented Student, Faculty and Admin RBAC with five permission levels: PUBLIC, INTERNAL, FACULTY_ONLY, CONFIDENTIAL and ADMIN_ONLY. Added keyword, regex and local semantic sensitivity detection, confidentiality-aware summarisation, controlled sharing, human confirmation for sensitive sharing, mandatory manual override rationale, explanation of decisions, configurable policies through `rules.json`, and a privacy-aware audit trail. The project includes a Streamlit application, synthetic dataset, dataset generator, experiment notebook, failure analysis and technical documentation.

## Review 1 Improvements Completed
1. **Semantic sensitivity detection:** Added local contextual TF-IDF similarity, sensitive phrase/entity rules and configurable semantic prototypes in addition to keyword/regex detection.
2. **Baseline comparison:** Implemented baseline versus protected evaluation with leakage rate, leakage reduction, precision, recall and F1 metrics.
3. **Configurable policy store:** Moved RBAC, sensitivity rules, thresholds and experiment targets into `rules.json`.

## Current Workflow
**User Role → Document Selection → Access Control → Sensitive Content Detection → Safe Summarisation / Sharing Decision → Human Confirmation if Required → Audit Record**

Unauthorized summaries are blocked before content is returned. Sensitive sharing enters a human-review state. Manual overrides require confirmation and a mandatory reason.

## Quantitative Evaluation
Synthetic evaluation uses 20 documents, 60 role-document cases and 22 unauthorized cases.

- Baseline leakage: **68.18%**
- Protected leakage: **0%**
- Leakage reduction: **100%**
- Precision: **86.67%**
- Recall: **100%**
- F1-score: **92.86%**
- False positives: **6**
- False negatives: **0**

Configured targets are 0% leakage, 80% precision and 90% recall. The protected synthetic evaluation meets all three targets.

## Testing
- Functional/security suite: **24/24 PASS**
- Leakage safety suite: **8/8 PASS**
- Error-boundary suite: **12/12 PASS**

The tests cover RBAC, sensitive detection, unauthorized summaries, sharing governance, semantic cases, malformed policy handling, invalid requests, missing detector results and audit sanitisation.

## Review 2 Documentation Improvements
The project now contains granular test documentation, an error-boundary specification, code comments/docstrings on security-critical modules, callable service/API boundary documentation, CSV/policy/audit schemas, and a final review checklist. The current prototype does not expose REST endpoints and does not use an external database; these boundaries are explicitly documented rather than falsely claiming unsupported components.

## Limitations and Next Steps
The evaluation uses synthetic data and lightweight local semantic detection. Future production work includes adversarial/red-team testing, calibrated thresholds, validated NER, larger stakeholder validation, encryption, database-backed tamper-evident audit storage, formal privacy/security review and deployment monitoring.
