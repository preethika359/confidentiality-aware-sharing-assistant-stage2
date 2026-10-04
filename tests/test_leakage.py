import sys
from pathlib import Path
import sys
ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_FOR_IMPORT))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules.access_control import check_access
from modules.detector import detect_sensitive_content
from modules.summarizer import generate_safe_summary
from modules.sharing import create_sharing_request, evaluate_sharing_request

# 1: unauthorised confidential summary must fail closed
content = "Student STU001 is under disciplinary investigation. This information is strictly confidential."
sens = detect_sensitive_content(content)
assert not check_access("Student", "CONFIDENTIAL")["allowed"]
summary = generate_safe_summary("Student", content, sens, access_allowed=False)
assert "STU001" not in summary and "disciplinary investigation" not in summary
print("PASS 1: unauthorised sensitive summary blocked")

# 2: authorised admin may receive sensitive summary
assert check_access("Admin", "CONFIDENTIAL")["allowed"]
admin_summary = generate_safe_summary("Admin", content, sens, access_allowed=True)
assert "disciplinary investigation" in admin_summary
print("PASS 2: authorised admin summary generated")

# 3: public summary remains available
public = "Semester examination starts on June 10. Students must report 30 minutes before the exam."
ps = detect_sensitive_content(public)
assert check_access("Student", "PUBLIC")["allowed"]
assert "Semester examination starts" in generate_safe_summary("Student", public, ps, True)
print("PASS 3: public summary generated")

# 4: unauthorised target blocks sharing
req = create_sharing_request("Faculty", "DOC005", "Faculty Salary Revision", "Student")
result = evaluate_sharing_request(req, check_access("Faculty", "ADMIN_ONLY"), check_access("Student", "ADMIN_ONLY"), detect_sensitive_content("Faculty salary revision details are restricted to university administrators."))
assert result["status"] == "Blocked"
print("PASS 4: unauthorised target sharing blocked")

# 5: sensitive sharing requires review
req = create_sharing_request("Admin", "DOC004", "Student Disciplinary Case", "Faculty")
result = evaluate_sharing_request(req, check_access("Admin", "CONFIDENTIAL"), check_access("Faculty", "CONFIDENTIAL"), sens)
assert result["status"] == "Blocked"  # target is not authorised under current policy
print("PASS 5: sensitive confidential target blocked by policy")

# 6: faculty-only sharing to faculty enters review
req = create_sharing_request("Admin", "DOC008", "Staff Performance", "Faculty")
result = evaluate_sharing_request(req, check_access("Admin", "FACULTY_ONLY"), check_access("Faculty", "FACULTY_ONLY"), detect_sensitive_content("Faculty performance review information is available only to authorised faculty members and administrators."))
assert result["status"] == "Review Required"
print("PASS 6: high-impact sensitive sharing enters review")

# 7: detector catches student ID and email
x = detect_sensitive_content("Student STU245 can be contacted at student245@example.edu.")
assert x["sensitive"] and any("stu245" in i.lower() for i in x["items"])
print("PASS 7: PII-like patterns detected")

# 8: empty input is safe
assert detect_sensitive_content("")["sensitive"] is False
assert detect_sensitive_content(None)["items"] == []
print("PASS 8: empty input handled safely")

print("\nALL 8 CORE SAFETY TESTS PASSED")
