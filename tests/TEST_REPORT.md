# Test Execution Report

## Environment

Python project with Streamlit, pandas, scikit-learn and spaCy dependencies.

## Functional/Security Suite

Command:

```bash
python tests/test_20_cases.py
```

Result: **24/24 PASS**

Coverage includes RBAC, unknown roles, empty/None input, ID/email detection, semantic paraphrases, case variation, multi-pattern detection, unauthorized summary blocking, authorized administrative summaries, sharing governance, explanation evidence and unknown permission labels.

## Leakage Safety Suite

Command:

```bash
python tests/test_leakage.py
```

Result: **8/8 PASS**

Coverage includes unauthorized sensitive summaries, authorized administration, public summaries, unauthorized target sharing, sensitive sharing review, PII-like patterns and empty input.

## Error-Boundary Suite

Command:

```bash
python tests/test_error_boundaries.py
```

Result: **12/12 PASS**

Coverage includes missing policy files, invalid policy schema, unknown roles, missing sensitivity results, invalid sharing requests and privacy-aware audit storage.

## Experiment

Command:

```bash
python experiments/run_experiment.py
```

Result:

- 20 documents.
- 60 role-document cases.
- 22 unauthorized cases.
- Baseline leakage: 68.18%.
- Protected leakage: 0.00%.
- Leakage reduction: 100%.
- Precision: 86.67%.
- Recall: 100%.
- F1: 92.86%.
- False positives: 6.
- False negatives: 0.

## Interpretation

The protected workflow met the configured zero-leakage, precision and recall targets on the synthetic evaluation set. False positives remain the main detection error and should be calibrated before production deployment.
