# Test Plan and Unit-Test Documentation

## Scope

The test suite validates RBAC, sensitivity detection, confidentiality-aware summarisation, sharing governance, configuration boundaries, and failure handling.

## Test Suites

| Suite | File | Coverage |
|---|---|---|
| Functional/security | `test_20_cases.py` | 24 deterministic access, detector, summary, sharing and policy cases. |
| Leakage safety | `test_leakage.py` | Sensitive summary and sharing leakage boundaries. |
| Error boundaries | `test_error_boundaries.py` | Missing policy, invalid policy schema, unknown roles, invalid requests, missing detector results and fail-closed behaviour. |

## Expected Commands

```bash
python tests/test_20_cases.py
python tests/test_leakage.py
python tests/test_error_boundaries.py
python experiments/run_experiment.py
```

## Test Design

### Access control
- Authorized role is allowed.
- Unauthorized role is denied.
- Unknown role is denied.
- Unknown permission label is denied.

### Detection
- None and empty input are safe.
- IDs and email patterns are detected.
- Paraphrased salary, performance, financial and medical information is detected.
- Case variations and multiple patterns are handled.

### Governance
- Unauthorized summary requests are blocked before content output.
- Unauthorized sharing is blocked.
- Sensitive sharing enters human-review state.
- Manual override requires confirmation and rationale in the Streamlit workflow.

### Error boundaries
- Missing policy configuration produces a controlled error.
- Invalid policy schema produces a controlled error.
- Missing sensitivity results fail closed.
- Invalid sharing requests fail closed.
- Unknown roles cannot bypass sharing controls.

## Security Boundary

The test suite uses synthetic documents only. Passing the suite demonstrates the tested behaviours; it is not a production security certification.
