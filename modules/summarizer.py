"""Simple deterministic summarisation with confidentiality gates."""


def _sentences(content):
    """Split synthetic document text into simple sentence units."""
    return [s.strip() for s in str(content).replace("!", ".").replace("?", ".").split(".") if s.strip()]


def generate_safe_summary(user_role, content, sensitive_result, access_allowed=True):
    """Fail-closed summary generation: authorization is checked before content output."""
    if not content:
        return "No summary available."
    if not access_allowed:
        return "Summary blocked: your role is not authorised for this document."
    if not isinstance(sensitive_result, dict):
        return "Summary blocked: sensitivity evaluation is unavailable."

    sentences = _sentences(content)
    if sensitive_result.get("sensitive") and user_role != "Admin":
        safe = []
        sensitive_items = [str(x).lower() for x in sensitive_result.get("items", [])]
        for sentence in sentences:
            low = sentence.lower()
            if not any(item in low for item in sensitive_items):
                safe.append(sentence)
        if safe:
            return "Safe Summary: " + safe[0] + ". Restricted details have been removed."
        return "Summary generated without restricted details. Sensitive information has been withheld."

    prefix = "Administrative Summary: " if user_role == "Admin" and sensitive_result.get("sensitive") else "Safe Summary: "
    return prefix + ". ".join(sentences[:2]) + ("." if sentences else "")
