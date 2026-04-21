# Atomic_chat

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Atomic_chat subsystem handles **12 routes** and touches: auth.

## Routes

- `POST` `/contexts` → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `GET` `/contexts/{opord_number}` params(opord_number) → out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `PATCH` `/contexts/{opord_number}` params(opord_number) → out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `POST` `/contexts/search` → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `POST` `/workflows/execute` → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `POST` `/scholarly-pdfs/upload` → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `POST` `/scholarly-pdfs/search` → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `GET` `/shifts/{shift_number}/contexts` params(shift_number) → out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `POST` `/shifts/{shift_number}/clear-memory` params(shift_number) → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `GET` `/export/{opord_number}` params(opord_number) → out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `POST` `/export/bulk` → in: CreateContextRequest, out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`
- `GET` `/export/preview` → out: ThreadExportResponse [auth, upload]
  `archive/broken/aiyou_fastapi_src/atomic_chat.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/broken/aiyou_fastapi_src/atomic_chat.py`

---
_Back to [overview.md](./overview.md)_
