"""Fail-closed role-based access control driven by rules.json."""
import json
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parents[1] / "rules.json"


def load_rules():
    """Load the external policy store and validate its required structure."""
    try:
        rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Policy configuration cannot be loaded: {exc}") from exc
    if not isinstance(rules, dict) or not isinstance(rules.get("permission_levels"), dict):
        raise RuntimeError("Policy configuration is invalid: permission_levels is required.")
    return rules


def check_access(user_role, permission_label):
    """Return a deterministic, fail-closed access decision."""
    rules = load_rules()
    allowed_roles = rules.get("permission_levels", {}).get(permission_label, [])
    allowed = isinstance(user_role, str) and user_role in allowed_roles
    if permission_label not in rules.get("permission_levels", {}):
        reason = f"Permission label '{permission_label}' is unknown; access is denied by default."
    elif allowed:
        reason = f"Role '{user_role}' is authorised for '{permission_label}' content."
    else:
        reason = f"Role '{user_role}' is NOT authorised for '{permission_label}' content."
    return {
        "allowed": allowed,
        "reason": reason,
        "rule": f"permission_levels.{permission_label}",
        "allowed_roles": allowed_roles,
        "policy_version": rules.get("policy_version", "unknown"),
    }


def explain_decision(user_role, permission_label, sensitive_result=None):
    """Expose policy/evidence metadata without changing the access decision."""
    access = check_access(user_role, permission_label)
    evidence = []
    if sensitive_result and sensitive_result.get("sensitive"):
        # UI may show evidence to the current authorised reviewer; audit storage is
        # separately sanitised in app.py and never stores these raw values.
        evidence = sensitive_result.get("items", [])
    return {
        "allowed": access["allowed"],
        "policy_rule": access["rule"],
        "policy_version": access["policy_version"],
        "authorised_roles": access["allowed_roles"],
        "sensitive_evidence": evidence,
        "reason": access["reason"],
    }
