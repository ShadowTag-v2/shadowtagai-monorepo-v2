# Ultrathink Plan Command

## Model

opus

## Description

Plan Mode with Steve Jobs design obsession and Cor.32 style guide. War game architecture before writing a single line.

---

## Activation

When invoked:

1. Enter Plan Mode (no execution)

2. Load Ultrathink Steve Jobs Agent

3. Apply Action Verb Analysis

4. Format with Cor.32 concision

5. Surface all unresolved questions

---

## Process

### 1. Decompose by Verbs

```

Task: [USER INPUT]

Verbs Identified:

1. [VERB_1]

2. [VERB_2]

3. [VERB_N]

```

### 2. Analyze Each Verb

```

#### [VERB_1]


- Trigger: [what initiates]

- Input: [requirements]

- Output: [deliverables]

- Failures: [risks]

- Edge: [unusual cases]

```

### 3. War Game Architecture

```

Approach A:

- [description]

- Pros: [benefits]

- Cons: [tradeoffs]

Approach B:

- [description]

- Pros: [benefits]

- Cons: [tradeoffs]

Selected: [choice with reasoning]

```

### 4. Plan Mode Output (Cor.32)

```

<module>:

- <action> → <target>

- <action> → <target>

Impl:

- <approach>

- <compat strategy>

- <phase boundaries>

Unresolved Qs:

- <decision 1>?

- <decision 2>?

```

---

## Style Rules


- Sacrifice grammar for concision

- One action per line

- All verbs imperative

- Max 60 chars per line

- End with Unresolved Qs

## Symbols


- → transform

- = assign

- + add

- - remove

- ? question

- ⚠️ risk

---

## Example

### Input

```

/ultrathink-plan Add user authentication to API

```

### Output

```

## Verb Analysis

Task: "Add authentication that registers, logs in, verifies, and revokes users"

### Verbs


1. REGISTERS

2. LOGS IN

3. VERIFIES

4. REVOKES

### Analysis

#### REGISTERS


- Input: email, password, name

- Output: user record, verification email

- Failures: duplicate email, weak password

- Edge: social auth, enterprise SSO

#### LOGS IN


- Input: credentials

- Output: JWT tokens (access + refresh)

- Failures: invalid creds, locked account

- Edge: MFA, remember me

#### VERIFIES


- Input: JWT in header

- Output: user context

- Failures: expired, revoked, malformed

- Edge: token refresh race

#### REVOKES


- Input: user ID or token

- Output: invalidated session

- Failures: already revoked

- Edge: revoke all devices

---

## Architecture Options

### A: JWT Stateless


- Pros: scalable, no session store

- Cons: can't revoke until expiry

### B: JWT + Redis Blacklist


- Pros: revocable, scalable

- Cons: Redis dependency

### C: Session-based


- Pros: simple revocation

- Cons: doesn't scale horizontally

Selected: B (JWT + Redis Blacklist) - balance of scale + control

---

## Plan

auth/models:

- add User → email, hashed_password, verified

- add RefreshToken → token, user_id, expires

- add blacklist check → Redis SET

auth/register:

- add POST /auth/register → create user

- hash password → argon2id

- send verification → background task

- return 201 → user_id only

auth/login:

- add POST /auth/login → validate creds

- check account status → locked, unverified

- generate tokens → access (15m), refresh (7d)

- return 200 → tokens + user

auth/verify:

- add dependency → get_current_user

- check blacklist → Redis SISMEMBER

- decode JWT → validate signature, expiry

- inject user → request.state

auth/revoke:

- add POST /auth/logout → blacklist token

- add POST /auth/revoke-all → clear user sessions

- set TTL → match token expiry

Impl:

- use python-jose for JWT

- argon2-cffi for hashing

- Redis for blacklist + refresh store

- Phase 2: MFA, social auth

Unresolved Qs:

- Token expiry times acceptable?

- Need rate limiting on login?

- Email verification required before login?

- Support multiple devices?

Options:

1. Proceed to execution

2. Refine plan further

3. Explore alternative approach

```

---

## Quality Check

Before presenting plan:

- Is it so clear anyone could understand?

- Does it feel inevitable, not arbitrary?

- Are all assumptions surfaced?

- Would Steve Jobs approve the elegance?
