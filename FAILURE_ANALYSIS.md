# Failure-Mode Analysis

| Failure mode | Example | Control | Evidence |
|---|---|---|---|
| Keyword miss due to paraphrase | “employee compensation package” | Local contextual similarity + configurable prototypes | Functional cases 11–14 |
| Sensitive identifier | `STU900` | Regex detector | Case 09 |
| Contact disclosure | `test@example.edu` | Regex + policy rules | Case 10 |
| Case variation | Uppercase disciplinary phrase | Case-insensitive matching | Case 15 |
| Multiple patterns | ID + email + salary | Multi-layer aggregation | Case 16 |
| Unauthorized summary | Student requests confidential case | Access gate before summarisation | Case 17 + leakage suite |
| Unauthorized sharing | Target role lacks permission | RBAC sharing gate | Case 19 + leakage suite |
| High-impact sensitive sharing | Authorized requester shares sensitive content | Human review state | Case 20 + leakage suite |
| Empty input | `None`, `""`, whitespace | Safe defaults | Functional + error-boundary suites |
| Unknown policy label | `DOES_NOT_EXIST` | Fail-closed access | Case 24 |
| Missing policy | Rules file unavailable | Controlled configuration error | Error-boundary case 03 |
| Invalid policy schema | Missing `permission_levels` | Controlled configuration error | Error-boundary case 04 |
| Missing sensitivity result | Detector result unavailable | Summary/sharing blocked | Error-boundary cases 08 and 10 |
| Invalid sharing request | Missing/unknown roles | Sharing blocked | Error-boundary cases 09 and 11 |
| Audit disclosure | Raw PII/salary evidence | Metadata-only audit schema | Error-boundary case 12 |
| Semantic false positive | Benign text resembles sensitive prototype | Precision measurement + threshold calibration | Experiment: 6 FPs |
| Semantic false negative | Context not represented by prototypes | Recall measurement + future model improvement | Experiment: 0 FNs on current synthetic set |

## Quantitative Error Analysis

Synthetic experiment results:

- True positives: **39**
- False positives: **6**
- False negatives: **0**
- Precision: **86.67%**
- Recall: **100%**
- F1: **92.86%**

The main remaining error type is contextual false positive detection. This is intentionally safer than silently missing sensitive information, but production deployment would require threshold calibration against representative university data and human review for high-impact actions.

## Security Boundary

The audit trail was hardened so that raw detector evidence is not persisted. It records evidence count and presence only. This prevents the audit file from becoming a secondary copy of confidential content.

All validation uses synthetic data. The results are evidence of the tested implementation, not a production security guarantee.
