# Presentation Outline — 10 Slides

1. **Problem** — informal policy distribution creates accidental disclosure risk.
2. **Objective** — summarise/share while enforcing document and role boundaries.
3. **Workflow** — request → access rule → sensitivity detection → human review → audit.
4. **Roles & policy labels** — Student, Faculty, Admin; five configurable permission levels.
5. **Prototype** — Streamlit dashboard, explanation layer, safe summary, sharing workflow.
6. **High-impact safeguard** — sensitive sharing requires human confirmation + override reason.
7. **Baseline experiment** — naive summariser vs protected workflow across every document-role pair.
8. **Failure cases** — unauthorised confidential access, unauthorised target role, missing override reason, indirect/regex-sensitive content.
9. **Results & limitations** — show generated `metrics.json`, error cases, and synthetic-data limitation.
10. **Next steps** — larger adversarial dataset, semantic detector, real stakeholder study, stronger audit storage.
