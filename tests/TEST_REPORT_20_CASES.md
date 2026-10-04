# Stage-2 Functional Validation Report

## Result

Command:

```bash
python tests/test_20_cases.py
```

**24/24 PASS — 100%**

The suite intentionally exceeds the earlier 16-case milestone and covers RBAC, semantic/context detection, edge inputs, summarisation boundaries, sharing governance, explanations and configurable-policy behaviour.

| Area | Cases |
|---|---:|
| RBAC / permission boundaries | 01–06 |
| None/empty input handling | 07–08 |
| Sensitive detection and paraphrases | 09–16 |
| Summary access boundary | 17–18 |
| Sharing governance / human review | 19–21 |
| Evidence, semantic layer and config smoke tests | 22–24 |

## Representative edge cases

- `None` and empty strings do not crash the detector.
- Case variation such as `DISCIPLINARY INVESTIGATION` is detected.
- Multiple sensitive patterns in one sentence are detected.
- Paraphrased salary, performance, finance and medical disclosures are detected through contextual matching.
- Unauthorised summaries fail closed.
- Sensitive sharing cannot silently bypass human review.
- Unknown roles and unknown permission labels are denied.

## Evidence

The console output ends with:

`ALL 24 TEST CASES PASSED`

These are synthetic academic validation tests, not a production security certification.
