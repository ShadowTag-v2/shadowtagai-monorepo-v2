# Enterprise_compliance_api

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Enterprise_compliance_api subsystem handles **4 routes** and touches: auth, db.

## Routes

- `POST` `/certificate` → in: ComplianceCertificateRequest, out: ComplianceCertificate [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `POST` `/batch` → in: ComplianceCertificateRequest, out: ComplianceCertificate [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `GET` `/dashboard` → out: ComplianceCertificate [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `GET` `/audit/{content_id}` params(content_id) → out: ComplianceCertificate [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`

---
_Back to [overview.md](./overview.md)_