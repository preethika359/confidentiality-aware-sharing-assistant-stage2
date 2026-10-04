# API and Data Schema Documentation

## API / Integration Boundary

The current prototype is a **Streamlit application with local Python modules**. It does not expose HTTP/REST API endpoints and does not require an external API service.

The main callable service boundaries are:

| Module | Function | Purpose |
|---|---|---|
| `modules/access_control.py` | `load_rules()` | Loads and validates `rules.json`. |
| `modules/access_control.py` | `check_access(role, permission)` | Returns a fail-closed RBAC decision. |
| `modules/access_control.py` | `explain_decision(...)` | Returns policy/evidence explanation metadata. |
| `modules/detector.py` | `detect_sensitive_content(text)` | Runs keyword, regex and semantic detection. |
| `modules/summarizer.py` | `generate_safe_summary(...)` | Generates a summary only after authorization. |
| `modules/sharing.py` | `create_sharing_request(...)` | Creates a controlled sharing request. |
| `modules/sharing.py` | `evaluate_sharing_request(...)` | Applies requester, target and sensitivity gates. |

If a production REST API is added later, these functions are the service-layer contract to expose through authenticated endpoints. No API is claimed in the current prototype.

## Document Dataset Schema

`data/documents.csv` is the synthetic document source.

| Column | Type | Meaning |
|---|---|---|
| `document_id` | string | Unique document identifier, e.g. `DOC001`. |
| `title` | string | Human-readable document title. |
| `permission_label` | categorical | `PUBLIC`, `INTERNAL`, `FACULTY_ONLY`, `CONFIDENTIAL`, or `ADMIN_ONLY`. |
| `content` | text | Synthetic university policy/document content. |
| `ground_truth_sensitive` | integer | Evaluation label: `1` sensitive, `0` non-sensitive. |
| `sensitive_category` | categorical | Synthetic category such as `disciplinary`, `performance`, `financial`, or `none`. |

## Policy Schema

`rules.json` contains:

- `policy_version`
- `permission_levels`
- `role_hierarchy`
- `high_impact_actions`
- `sensitive_summary_policy`
- `sensitivity.keywords`
- `sensitivity.regex_patterns`
- `sensitivity.ner_sensitive_phrases`
- `sensitivity.semantic_prototypes`
- `sensitivity.semantic_threshold`
- `sensitivity.high_severity_terms`
- `sensitivity.medium_severity_terms`
- `experiment` targets

## Audit Schema

`data/audit_log.csv` is local runtime output and is excluded from Git.

The audit trail stores decision metadata:

`timestamp, action, user_role, document_id, document_title, target_role, decision, reason, evidence_count, evidence_recorded`

Raw sensitive detector values are intentionally **not** stored in the audit log. This prevents the audit trail from becoming a secondary sensitive-data repository.

## Storage Boundary

The current prototype uses CSV and JSON files only. No relational database is required. A production deployment should migrate audit storage to an access-controlled database with encryption, retention rules, and tamper-evident logging.
