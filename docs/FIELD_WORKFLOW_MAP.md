# Field Workflow Map

```text
Policy update arrives
        |
        v
[Document + Permission Label]
        |
        v
[User Role + Sharing Target]
        |
        v
[1. Access Rule Check] ---- denied ----> BLOCK + EXPLANATION + AUDIT
        |
      allowed
        v
[2. Sensitive Content Detection]
        |
   +----+----+
   |         |
 none      sensitive
   |         |
   v         v
summary   REVIEW REQUIRED
   |         |
   |      human confirmation?
   |       /          \
   |     no            yes
   |     |              |
   |  BLOCK + AUDIT   override reason required
   |                    |
   |               approve + AUDIT
   v                    v
[Share / Summary Output]
        |
        v
[Persistent Decision Trail]
```

## Actors
- Student: public/internal access according to `rules.json`.
- Faculty: public/internal/faculty-only access according to `rules.json`.
- Admin: all configured levels in the synthetic prototype.
- Human reviewer: confirms high-impact sensitive sharing.

## Evidence shown to users
- Policy rule and version.
- Authorised roles.
- Detected sensitive evidence.
- Decision reason.
- Manual override reason when applicable.
