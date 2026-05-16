# Skills Supply Chain Doctrine

## Why this exists
Open skill ecosystems are strategically valuable and operationally dangerous.

## Research takeaways
- Public skill ecosystems can compress task steps and improve outcomes.
- Public skill ecosystems also carry a non-trivial malicious or vulnerable skill rate.
- Executable skills are riskier than instruction-only skills.

## Policy
1. Default-deny third-party executable skills.
2. Separate instruction-only skills from executable skills.
3. Require static review before install.
4. Require permission scoping per skill.
5. Vendor or pin approved skills into a local registry.
6. Block network, filesystem, secret, and subprocess access unless explicitly granted.
7. Prefer official docs and first-party samples over random marketplace imports.

## Approved pattern
- Mine ideas from public skills.
- Rebuild locally.
- Audit locally.
- Vendor locally.
