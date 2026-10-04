import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent

# Synthetic only: no real student/faculty data.
documents = [
    ("DOC001", "Examination Policy", "PUBLIC", "Semester examination starts on June 10. Students must report 30 minutes before the exam."),
    ("DOC002", "Internal Timetable", "INTERNAL", "The university internal assessment schedule will be published next week."),
    ("DOC003", "Faculty Meeting", "FACULTY_ONLY", "Faculty meeting will be conducted on June 5. Internal staff evaluation will be discussed."),
    ("DOC004", "Student Disciplinary Case", "CONFIDENTIAL", "Student STU001 is under disciplinary investigation. This information is strictly confidential."),
    ("DOC005", "Faculty Salary Revision", "ADMIN_ONLY", "Faculty salary revision details are restricted to university administrators."),
    ("DOC006", "Library Policy", "PUBLIC", "The library is open from 8 AM to 6 PM on working days."),
    ("DOC007", "Student Attendance", "INTERNAL", "Students must maintain the minimum attendance requirement according to university regulations."),
    ("DOC008", "Staff Performance", "FACULTY_ONLY", "Faculty performance review information is available only to authorised faculty members and administrators."),
    ("DOC009", "Scholarship Policy", "PUBLIC", "Eligible students can apply for university scholarships before the announced deadline."),
    ("DOC010", "Administrative Budget", "ADMIN_ONLY", "The annual departmental budget contains restricted financial information for administrators."),
    ("DOC011", "Student Contact Test", "CONFIDENTIAL", "Student STU245 can be contacted at student245@example.edu. The record is confidential."),
    ("DOC012", "Mixed Policy Notice", "FACULTY_ONLY", "The workshop is on Friday. Staff evaluation notes must remain restricted."),
]

out = BASE / "documents.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["document_id", "title", "permission_label", "content"])
    writer.writerows(documents)
print(f"Generated {len(documents)} synthetic documents: {out}")
