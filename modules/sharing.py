"""Controlled document-sharing workflow with fail-closed validation."""

VALID_ROLES = {"Student", "Faculty", "Admin"}


def create_sharing_request(requester_role, document_id, document_title, target_role):
    """Create a normalized sharing request; validation happens during evaluation."""
    return {
        "requester_role": requester_role,
        "document_id": document_id,
        "document_title": document_title,
        "target_role": target_role,
        "status": "Pending",
    }


def evaluate_sharing_request(request, requester_access, target_access, sensitive_result):
    """Apply requester, recipient, and sensitivity gates in that order."""
    if not isinstance(request, dict):
        return {"status": "Blocked", "reason": "Invalid sharing request.", "high_impact": False}
    if request.get("requester_role") not in VALID_ROLES or request.get("target_role") not in VALID_ROLES:
        return {"status": "Blocked", "reason": "Unknown requester or target role.", "high_impact": False}
    if not requester_access.get("allowed", False):
        return {"status": "Blocked", "reason": "Requester is not authorised to share this document.", "high_impact": False}
    if not target_access.get("allowed", False):
        return {"status": "Blocked", "reason": "Target role is not authorised to receive this document.", "high_impact": False}
    if not isinstance(sensitive_result, dict):
        return {"status": "Blocked", "reason": "Sensitivity result is unavailable; sharing is denied by default.", "high_impact": False}
    if sensitive_result.get("sensitive"):
        return {"status": "Review Required", "reason": "Sensitive content detected. Human confirmation is required before sharing.", "high_impact": True}
    return {"status": "Approved", "reason": "Requester, target role, and content checks passed.", "high_impact": False}
