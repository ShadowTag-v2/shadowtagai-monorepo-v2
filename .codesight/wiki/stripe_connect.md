# Stripe_connect

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Stripe_connect subsystem handles **2 routes** and touches: auth, payment.

## Routes

- `POST` `/onboard` → in: ConnectOnboardRequest, out: ConnectOnboardResponse [auth, payment]
  `apps/counselconduit/api/stripe_connect.py`
- `POST` `/create-payment-intent` → in: ConnectOnboardRequest, out: ConnectOnboardResponse [auth, payment]
  `apps/counselconduit/api/stripe_connect.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/stripe_connect.py`

---
_Back to [overview.md](./overview.md)_
