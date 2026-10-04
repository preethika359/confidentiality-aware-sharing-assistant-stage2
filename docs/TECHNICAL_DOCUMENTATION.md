# Technical Documentation

## 1. System Architecture

`Streamlit UI → Policy Store → RBAC → Hybrid Sensitivity Detector → Summary/Sharing Gate → Explanation → Audit Trail`

The application is intentionally modular so that policy, detection, summarisation, sharing and audit concerns can be tested independently.

## 2. Module Responsibilities

### `modules/access_control.py`
- Loads `rules.json`.
- Validates that `permission_levels` exists.
- Performs fail-closed role/permission checks.
- Produces explanation metadata.

### `modules/detector.py`
- Keyword matching.
- Regex detection for identifiers, email, phone/salary patterns.
- Local sensitive phrase/entity matching.
- Local TF-IDF contextual similarity against configurable sensitive prototypes.
- Returns evidence, detection layers and severity.

### `modules/summarizer.py`
- Checks authorization before returning content.
- Blocks unauthorized summaries.
- Withholds detected sensitive sentence content for non-admin authorized users.
- Produces a deterministic synthetic summary suitable for evaluation.

### `modules/sharing.py`
- Validates requester and target roles.
- Blocks unauthorized sharing.
- Returns `Review Required` for sensitive sharing.
- Requires the Streamlit layer to collect human confirmation and a mandatory override reason.

### `modules/audit.py`
- Builds and persists audit metadata.
- Stores evidence count/flag rather than raw detector values.
- Keeps sensitive content from becoming a second repository inside the audit trail.

## 3. Policy Store

`rules.json` contains permission levels, role hierarchy, high-impact actions, sensitivity keywords, regex patterns, semantic phrases, semantic prototypes, threshold, severity terms and experiment targets.

No role decision is hard-coded into the access-control policy logic.

## 4. Error Boundaries

The system is fail-closed at important boundaries:

1. Missing policy file → controlled configuration error.
2. Invalid policy JSON/schema → controlled configuration error.
3. Unknown role → denied.
4. Unknown permission label → denied.
5. Missing sensitivity result → summary/sharing blocked.
6. Invalid sharing request → blocked.
7. Sensitive sharing → human review.
8. Missing manual override confirmation/reason → UI refuses approval.
9. Raw sensitive evidence → excluded from audit storage.

## 5. Data Model

The synthetic document table contains:

`document_id, title, permission_label, content, ground_truth_sensitive, sensitive_category`

Permission labels map to roles through `rules.json`.

The runtime audit table contains:

`timestamp, action, user_role, document_id, document_title, target_role, decision, reason, evidence_count, evidence_recorded`

No external database is required for the current prototype.

## 6. API Boundary

There are no HTTP/REST endpoints in the current version. The application exposes internal Python service functions documented in `docs/API_AND_DATA_SCHEMA.md`. A future API layer can wrap these functions behind authentication and authorization without changing the policy/detection core.

## 7. Experiment Design

Twenty synthetic documents and three roles produce 60 role-document cases. The experiment compares a naive first-sentence baseline with the protected workflow.

The leakage oracle checks whether sensitive source evidence reappears in an unauthorized summary. Detector metrics are calculated using the dataset's `ground_truth_sensitive` labels.

Measured results:

- Baseline leakage: 68.18%.
- Protected leakage: 0.00%.
- Leakage reduction: 100%.
- Precision: 86.67%.
- Recall: 100%.
- F1: 92.86%.
- False positives: 6.
- False negatives: 0.

The main measured error type is false positive contextual similarity. A production system should calibrate thresholds against representative data and use human review for high-impact decisions.

## 8. Governance

High-impact sensitive sharing is not automatically completed. The UI requires human confirmation and a mandatory override rationale. Decisions are logged for auditability, while raw sensitive values are not retained in the audit CSV.

## 9. Validation Boundary

All current tests and experiments use synthetic data. Passing the test suite demonstrates the implemented behaviours on the test set; it does not constitute a real-world security certification.
