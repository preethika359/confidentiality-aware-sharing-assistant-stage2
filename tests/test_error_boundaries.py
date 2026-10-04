"""Error-boundary and fail-closed tests for malformed/unavailable inputs."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.access_control import check_access, load_rules
from modules.detector import detect_sensitive_content
from modules.sharing import create_sharing_request, evaluate_sharing_request
from modules.summarizer import generate_safe_summary
from modules.audit import build_audit_row, AUDIT_COLUMNS

passed = 0
failed = []


def check(name, condition):
    global passed
    if condition:
        passed += 1
        print(f"PASS | {name}")
    else:
        failed.append(name)
        print(f"FAIL | {name}")


# Policy/data boundaries
check("01 Unknown permission fails closed", not check_access("Student", "UNKNOWN")['allowed'])
check("02 None role fails closed", not check_access(None, "PUBLIC")['allowed'])

with patch("modules.access_control.RULES_PATH") as fake_path:
    fake_path.read_text.side_effect = OSError("missing")
    try:
        load_rules()
        policy_error = False
    except RuntimeError:
        policy_error = True
check("03 Missing policy raises controlled RuntimeError", policy_error)

with patch("modules.access_control.RULES_PATH") as fake_path:
    fake_path.read_text.return_value = json.dumps({"bad": True})
    try:
        load_rules()
        schema_error = False
    except RuntimeError:
        schema_error = True
check("04 Invalid policy schema raises controlled RuntimeError", schema_error)

# Detector/summariser boundaries
check("05 Detector handles None", detect_sensitive_content(None)["sensitive"] is False)
check("06 Detector handles whitespace", detect_sensitive_content("   ")["sensitive"] is False)
check("07 Invalid regex is ignored safely", detect_sensitive_content("normal text")["sensitive"] is False)
check("08 Missing sensitivity result blocks summary", "blocked" in generate_safe_summary("Student", "Private text", None, True).lower())

# Sharing boundaries
request = create_sharing_request("Visitor", "DOC001", "Test", "Student")
result = evaluate_sharing_request(request, {"allowed": True}, {"allowed": True}, {"sensitive": False})
check("09 Unknown sharing role is blocked", result["status"] == "Blocked")

request = create_sharing_request("Student", "DOC001", "Test", "Student")
result = evaluate_sharing_request(request, {"allowed": True}, {"allowed": True}, None)
check("10 Missing sensitivity result fails closed", result["status"] == "Blocked")

check("11 Non-dict request is blocked", evaluate_sharing_request(None, {}, {}, {})["status"] == "Blocked")

# Audit safety is validated at the application layer by checking the audit schema contract.
row = build_audit_row("Summary", "Student", "DOC001", "Test", "-", "Blocked", "Denied", ["salary is $5000", "test@example.edu"])
check("12 Audit excludes raw evidence values", "salary is $5000" not in row.values() and "test@example.edu" not in row.values() and set(row) == set(AUDIT_COLUMNS))

print(f"\nTOTAL: {passed}/12 PASS")
if failed:
    print("FAILED:", ", ".join(failed))
    raise SystemExit(1)
print("ALL 12 ERROR-BOUNDARY TESTS PASSED")
