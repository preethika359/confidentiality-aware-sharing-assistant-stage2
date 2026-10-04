"""Privacy-aware audit trail writer."""
from datetime import datetime
from pathlib import Path
import pandas as pd

AUDIT_COLUMNS = [
    "timestamp", "action", "user_role", "document_id", "document_title",
    "target_role", "decision", "reason", "evidence_count", "evidence_recorded"
]


def build_audit_row(action, user_role, doc_id, title, target_role, decision, reason, evidence=None):
    """Build audit metadata while deliberately excluding raw sensitive evidence."""
    evidence = evidence or []
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "user_role": user_role,
        "document_id": doc_id,
        "document_title": title,
        "target_role": target_role,
        "decision": decision,
        "reason": reason,
        "evidence_count": len(evidence),
        "evidence_recorded": bool(evidence),
    }


def append_audit(path, row):
    """Append one audit row and create the CSV header when necessary."""
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    safe_row = {key: row.get(key, "") for key in AUDIT_COLUMNS}
    pd.DataFrame([safe_row]).to_csv(path, mode="a", header=not path.exists(), index=False)
