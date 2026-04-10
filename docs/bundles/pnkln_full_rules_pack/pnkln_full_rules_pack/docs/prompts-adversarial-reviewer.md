# Adversarial Reviewer Prompt

Act as an adversarial reviewer trying to break this app without access to source-control secrets.
Look for:

- enumeration
- privilege escalation
- IDOR
- unsafe direct route access
- insecure reset or recovery flows
- upload abuse
- replay or webhook abuse
- client-only authorization assumptions

Return:

1. attack paths
2. prerequisites
3. impact
4. smallest fixes
