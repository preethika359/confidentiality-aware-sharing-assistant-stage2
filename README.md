# Confidentiality-Aware Summarisation and Sharing Assistant

A Streamlit research prototype for a university environment where policy updates move through informal channels. The assistant enforces configurable access boundaries before document access, summarisation and sharing; explains decisions; requires human confirmation for high-impact actions; supports manual override with rationale; and retains a privacy-aware audit trail.

## Stage 2 / Review 2 Improvements

- RBAC for **Student, Faculty and Admin**.
- Five permission levels: `PUBLIC`, `INTERNAL`, `FACULTY_ONLY`, `CONFIDENTIAL`, `ADMIN_ONLY`.
- Hybrid sensitive-content detection using keywords, regex, local phrase/entity rules and local TF-IDF contextual similarity.
- External configurable policy store in `rules.json`.
- Fail-closed access and summarisation gates.
- Controlled sharing workflow with requester/target checks.
- Human confirmation for sensitive sharing.
- Mandatory manual-override reason.
- Explanation layer showing policy rule, authorized roles, reason and detected evidence in the UI.
- Privacy-aware audit trail: raw sensitive detector values are **not** written to the audit CSV.
- Synthetic leakage experiment and error analysis.
- Expanded functional, leakage and error-boundary tests.

## Architecture

```text
Streamlit UI
    |
    +--> External Policy Store (rules.json)
    |
    +--> RBAC / Access Control
    |
    +--> Hybrid Sensitivity Detector
    |       +-- Keyword rules
    |       +-- Regex rules
    |       +-- Local sensitive phrase/entity rules
    |       +-- TF-IDF semantic prototypes
    |
    +--> Safe Summarisation Gate
    |
    +--> Controlled Sharing Gate
    |       +-- Human confirmation
    |       +-- Manual override rationale
    |
    +--> Explanation Layer
    |
    +--> Privacy-Aware Audit Trail (local CSV)
```

## Project Workflow

**User Role → Document Selection → Access Control → Sensitive Content Detection → Safe Summarisation / Sharing Decision → Human Confirmation if Required → Audit Record**

## Evaluation Evidence

The reproducible synthetic experiment evaluates **20 documents × 3 roles = 60 role-document cases**, including 22 unauthorized cases.

| Metric | Measured result |
|---|---:|
| Baseline unauthorized leakage | **68.18%** |
| Protected unauthorized leakage | **0.00%** |
| Leakage reduction | **100%** |
| Detector precision | **86.67%** |
| Detector recall | **100%** |
| Detector F1 | **92.86%** |
| False positives | **6** |
| False negatives | **0** |

Targets configured in `rules.json`: 0% leakage, 80% precision and 90% recall. The protected synthetic evaluation meets all three targets.

These are synthetic evaluation results, not a production security certification.

## Testing

### Functional/security tests
`tests/test_20_cases.py` contains 24 deterministic cases covering RBAC, sensitive detection, summary boundaries, sharing governance, evidence reporting and unknown policy labels.

**Result: 24/24 PASS.**

### Leakage tests
`tests/test_leakage.py` validates unauthorized sensitive-summary blocking, authorized administration, public summaries, sharing boundaries, sensitive-sharing review, PII-like detection and empty input handling.

**Result: 8/8 PASS.**

### Error-boundary tests
`tests/test_error_boundaries.py` validates missing/invalid policy handling, unknown roles, missing sensitivity results, invalid sharing requests and audit sanitisation.

**Result: 12/12 PASS.**

Run all checks from the project root:

```bash
pip install -r requirements.txt
python tests/test_20_cases.py
python tests/test_leakage.py
python tests/test_error_boundaries.py
python experiments/run_experiment.py
streamlit run app.py
```

## Error Handling and Security Boundaries

The prototype is fail-closed:

- Unknown roles are denied.
- Unknown permission labels are denied.
- Missing or malformed policy configuration raises a controlled configuration error.
- Missing sensitivity results block summary/sharing decisions rather than bypassing controls.
- Invalid sharing requests are blocked.
- Sensitive sharing enters a human-review state.
- Manual override cannot be completed without confirmation and a reason.
- Raw sensitive detector values are excluded from the audit log.

## Configuration

`rules.json` controls permission levels, role hierarchy, sensitive keywords, regex patterns, semantic phrases, semantic prototypes, semantic threshold, severity terms and experiment targets.

Policies can therefore be changed without hard-coding role decisions into the application.

## Data Schema

`data/documents.csv` is synthetic and contains:

- `document_id`
- `title`
- `permission_label`
- `content`
- `ground_truth_sensitive`
- `sensitive_category`

The current prototype uses CSV/JSON storage and does not require a relational database.

## API / Integration Note

The current prototype does **not** expose HTTP/REST API endpoints. Its service-layer boundaries are Python functions in `modules/`. Detailed callable interfaces and the data/audit schema are documented in `docs/API_AND_DATA_SCHEMA.md`.

## Audit Trail

Runtime audit records are written to `data/audit_log.csv` and excluded from Git using `.gitignore`.

The audit schema stores:

`timestamp, action, user_role, document_id, document_title, target_role, decision, reason, evidence_count, evidence_recorded`

Raw sensitive values are intentionally not stored.

## Documentation

- `docs/TECHNICAL_DOCUMENTATION.md` — architecture, controls and experiment design.
- `docs/API_AND_DATA_SCHEMA.md` — callable service boundaries, CSV schema, policy schema and audit schema.
- `docs/TEST_PLAN.md` — granular unit/functional/error-boundary test documentation.
- `FAILURE_ANALYSIS.md` — failure modes, mitigations and error analysis.
- `USER_VALIDATION.md` — stakeholder validation protocol; no fabricated stakeholder responses are claimed.
- `docs/FIELD_WORKFLOW_MAP.md` — field workflow.
- `experiments/experiment_notebook.ipynb` — reproducible experiment notebook.
- `experiments/metrics.json` — generated metrics.
- `experiments/experiment_results.csv` — case-level evidence.

## Limitations and Future Work

The project uses synthetic university documents and a lightweight local semantic detector. Future production hardening should include calibrated thresholds, a validated NER model, adversarial/red-team testing, encryption, access-controlled database-backed immutable audit storage, formal privacy review, larger stakeholder validation and deployment monitoring.
