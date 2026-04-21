# Subscription

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Subscription subsystem handles **1 routes** and touches: auth, payment.

## Routes

- `POST` `/create-checkout-session` → in: CheckoutRequest [auth, payment]
  `archive/agent_debris/api/routes/subscription.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/api/routes/subscription.py`

---
_Back to [overview.md](./overview.md)_
