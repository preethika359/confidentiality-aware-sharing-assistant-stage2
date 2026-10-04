import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""24 deterministic functional/security tests for the prototype."""
from modules.access_control import check_access
from modules.detector import detect_sensitive_content
from modules.summarizer import generate_safe_summary
from modules.sharing import create_sharing_request, evaluate_sharing_request

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

# Access control
check("01 Student can access PUBLIC", check_access("Student", "PUBLIC")["allowed"])
check("02 Faculty can access FACULTY_ONLY", check_access("Faculty", "FACULTY_ONLY")["allowed"])
check("03 Student blocked from FACULTY_ONLY", not check_access("Student", "FACULTY_ONLY")["allowed"])
check("04 Faculty blocked from CONFIDENTIAL", not check_access("Faculty", "CONFIDENTIAL")["allowed"])
check("05 Admin can access ADMIN_ONLY", check_access("Admin", "ADMIN_ONLY")["allowed"])
check("06 Unknown role denied", not check_access("Visitor", "CONFIDENTIAL")["allowed"])

# Detector edge/semantic cases
check("07 None input safe", not detect_sensitive_content(None)["sensitive"])
check("08 Empty input safe", not detect_sensitive_content("")["sensitive"])
check("09 Student ID detected", detect_sensitive_content("Student STU900 is under review") ["sensitive"])
check("10 Email detected", detect_sensitive_content("Contact test@example.edu") ["sensitive"])
check("11 Salary paraphrase detected", detect_sensitive_content("The employee compensation package is private")["sensitive"])
check("12 Performance paraphrase detected", detect_sensitive_content("The staff appraisal discusses individual performance")["sensitive"])
check("13 Financial paraphrase detected", detect_sensitive_content("Private financial figures are restricted")["sensitive"])
check("14 Medical paraphrase detected", detect_sensitive_content("The student's medical details must remain private")["sensitive"])
check("15 Case variation detected", detect_sensitive_content("DISCIPLINARY INVESTIGATION is confidential")["sensitive"])
check("16 Multi-pattern detection", len(detect_sensitive_content("STU123 and user@example.edu salary information")["items"]) >= 2)

# Summary boundary
s = detect_sensitive_content("Student STU001 is under disciplinary investigation.")
check("17 Unauthorized summary blocked", "blocked" in generate_safe_summary("Student", "Student STU001 is under disciplinary investigation.", s, False).lower())
check("18 Authorized Admin summary available", "administrative" in generate_safe_summary("Admin", "Student STU001 is under disciplinary investigation.", s, True).lower())

# Sharing governance
req = create_sharing_request("Faculty", "DOC004", "Case", "Student")
result = evaluate_sharing_request(req, check_access("Faculty", "CONFIDENTIAL"), check_access("Student", "CONFIDENTIAL"), s)
check("19 Unauthorised requester blocked", result["status"] == "Blocked")

req2 = create_sharing_request("Admin", "DOC004", "Case", "Faculty")
result2 = evaluate_sharing_request(req2, check_access("Admin", "CONFIDENTIAL"), check_access("Faculty", "CONFIDENTIAL"), s)
check("20 High-impact sharing requires review", result2["status"] == "Blocked" or result2["status"] == "Review Required")

# Public sharing
pub = detect_sensitive_content("Library opens at 8 AM.")
req3 = create_sharing_request("Faculty", "DOC001", "Exam", "Student")
result3 = evaluate_sharing_request(req3, check_access("Faculty", "PUBLIC"), check_access("Student", "PUBLIC"), pub)
check("21 Non-sensitive public sharing approved", result3["status"] == "Approved")

# Explanation/configuration smoke checks
check("22 Detector reports evidence", bool(detect_sensitive_content("STU123 confidential")["items"]))
check("23 Detector exposes semantic/keyword layers", bool(detect_sensitive_content("employee compensation is private")["layers"]))
check("24 Unknown permission label denied", not check_access("Student", "DOES_NOT_EXIST")["allowed"])

print(f"\nTOTAL: {passed}/24 PASS")
if failed:
    print("FAILED:", ", ".join(failed))
    raise SystemExit(1)
print("ALL 24 TEST CASES PASSED")
