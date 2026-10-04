import json
from pathlib import Path
import sys
ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_FOR_IMPORT))
import pandas as pd
from modules.detector import detect_sensitive_content
from modules.summarizer import generate_safe_summary
from modules.access_control import check_access

ROOT = Path(__file__).resolve().parents[1]
DOCS = pd.read_csv(ROOT / "data" / "documents.csv")
ROLES = ["Student", "Faculty", "Admin"]


def baseline_summary(text):
    sentences = [s.strip() for s in str(text).replace("!", ".").replace("?", ".").split(".") if s.strip()]
    return (sentences[0] + ".") if sentences else ""


def token_leak(summary, source):
    """Leakage oracle for synthetic evaluation: checks known sensitive spans and identifiers."""
    s = str(summary).lower()
    src = str(source)
    candidates = []
    result = detect_sensitive_content(src)
    candidates.extend([str(x).lower() for x in result.get("items", [])])
    # Ground-truth identifiers are always leakage if reproduced.
    import re
    candidates.extend(re.findall(r"\bSTU\d+\b", src, flags=re.I))
    candidates.extend(re.findall(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", src, flags=re.I))
    return any(x and x in s for x in set(candidates))


rows = []
for _, row in DOCS.iterrows():
    for role in ROLES:
        access = check_access(role, row.permission_label)
        det = detect_sensitive_content(row.content)
        base = baseline_summary(row.content)
        safe = generate_safe_summary(role, row.content, det, access_allowed=access["allowed"])
        rows.append({
            "document_id": row.document_id,
            "role": role,
            "permission": row.permission_label,
            "ground_truth_sensitive": int(row.ground_truth_sensitive),
            "detected_sensitive": int(det["sensitive"]),
            "detector_layers": ",".join(det["layers"]),
            "authorised": bool(access["allowed"]),
            "baseline_leak": int((not access["allowed"]) and token_leak(base, row.content)),
            "protected_leak": int((not access["allowed"]) and token_leak(safe, row.content)),
            "baseline_summary": base,
            "protected_summary": safe
        })

out = pd.DataFrame(rows)
out.to_csv(ROOT / "experiments" / "experiment_results.csv", index=False)

# Detection precision / recall / F1 at document level.
tp = int(((out.ground_truth_sensitive == 1) & (out.detected_sensitive == 1)).sum())
fp = int(((out.ground_truth_sensitive == 0) & (out.detected_sensitive == 1)).sum())
fn = int(((out.ground_truth_sensitive == 1) & (out.detected_sensitive == 0)).sum())
precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

unauth = out[~out.authorised]
base_rate = float(unauth.baseline_leak.mean()) if len(unauth) else 0.0
safe_rate = float(unauth.protected_leak.mean()) if len(unauth) else 0.0

metrics = {
    "dataset_documents": int(len(DOCS)),
    "total_role_document_cases": int(len(out)),
    "unauthorised_cases": int(len(unauth)),
    "baseline_leakage_rate": round(base_rate, 4),
    "protected_leakage_rate": round(safe_rate, 4),
    "leakage_reduction_percent": round((1 - safe_rate / base_rate) * 100, 2) if base_rate else 100.0,
    "target_zero_leakage": 0.0,
    "protected_meets_zero_leakage_target": safe_rate == 0.0,
    "detector_true_positive": tp,
    "detector_false_positive": fp,
    "detector_false_negative": fn,
    "detector_precision": round(precision, 4),
    "detector_recall": round(recall, 4),
    "detector_f1": round(f1, 4),
    "target_precision": 0.80,
    "target_recall": 0.90,
    "semantic_layer_enabled": True
}
(ROOT / "experiments" / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(json.dumps(metrics, indent=2))
