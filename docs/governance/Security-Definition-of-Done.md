# Security Definition of Done

- Managed auth is used for production auth flows.
- Access tokens are short-lived and refresh tokens are rotated/revocable.
- Every external input is validated with typed schemas.
- Authorization is enforced server-side.
- Password reset and recovery flows resist enumeration and abuse.
- Uploads are validated by allow-list, size, and content/signature.
- Security headers are enabled.
- CSRF protection exists where cookies are used.
- Rate limits are appropriate for auth, write, export, and expensive routes.
- No secrets or PII are written to logs.
- Secret scan passes.
- Dependency remediation is reviewed, not blindly auto-fixed.
- Backups exist and restoration is testable.
- Test and production are isolated.
