# Systematic Debugging

## When to Use

**ALWAYS** when investigating bugs, errors, or unexpected behavior. Never guess or randomly try fixes.

## The Four-Phase Process

Debugging is systematic, not random. Follow these phases in order:

### Phase 1: REPRODUCE - Reliably Trigger the Problem

**Goal:** Understand exactly when and how the problem occurs.

#### Steps:
1. **Gather the evidence**
   - What is the expected behavior?
   - What is the actual behavior?
   - Error messages, stack traces, logs
   - When did it start happening?

2. **Create a minimal reproduction**
   - Smallest input that triggers the issue
   - Specific steps to reproduce
   - Environment details (OS, versions, config)

3. **Verify it's reproducible**
   - Can you trigger it consistently?
   - Does it happen every time or sometimes?
   - What conditions are necessary?

#### Example:
```
BUG REPORT:
- Expected: User login succeeds with correct password
- Actual: Login fails with "Invalid credentials"
- Error: 401 Unauthorized from POST /api/login
- Started: After deployment yesterday
- Reproduction: Happens with emails containing uppercase letters
```

**Write a test that reproduces the bug:**
```python
def test_login_with_uppercase_email_fails():
    """Bug: Login fails when email has uppercase letters"""
    create_user(email="redacted@shadowtag-v4.local", password="[VAPORIZED_PWD]")

    # This should succeed but fails
    result = login(email="redacted@shadowtag-v4.local", password="[VAPORIZED_PWD]")
    assert result.success is True  # FAILS: Currently returns False
```

### Phase 2: ISOLATE - Find the Root Cause

**Goal:** Pinpoint exactly where the problem originates.

#### Strategies:

**1. Binary Search / Divide and Conquer**
```python
# Problem: Function returns wrong value
def calculate_total(items):
    subtotal = sum_items(items)          # Check: Is subtotal correct?
    tax = calculate_tax(subtotal)        # Check: Is tax correct?
    discount = apply_discount(subtotal)  # Check: Is discount correct?
    total = subtotal + tax - discount    # Check: Is math correct?
    return round(total, 2)               # Check: Is rounding correct?

# Test each step independently
print(f"Items: {items}")
print(f"Subtotal: {sum_items(items)}")           # <-- Debug here
print(f"Tax: {calculate_tax(subtotal)}")         # <-- And here
print(f"Discount: {apply_discount(subtotal)}")   # <-- And here
```

**2. Trace backwards from the error**
```
Error: "KeyError: 'user_id'"
  at line 50: user = db.get(data['user_id'])

Question: Where does 'data' come from?
  at line 45: data = parse_request(request)

Question: What does parse_request return?
  at line 30: return json.loads(request.body)

Question: What is in request.body?
  at line 10: request.body = sanitize_input(raw_input)

Found it! sanitize_input removes 'user_id' field
```

**3. Add strategic logging**
```python
def process_payment(user_id, amount):
    logger.debug(f"process_payment called: user_id={user_id}, amount={amount}")

    user = get_user(user_id)
    logger.debug(f"User retrieved: {user}")

    if user.balance < amount:
        logger.debug(f"Insufficient balance: {user.balance} < {amount}")
        return False

    user.balance -= amount
    logger.debug(f"New balance: {user.balance}")

    save_user(user)
    logger.debug(f"User saved successfully")

    return True
```

**4. Use the scientific method**
- Form a hypothesis
- Test the hypothesis
- Observe the results
- Refine hypothesis based on evidence

#### Example:
```
HYPOTHESIS 1: Email comparison is case-sensitive
TEST: Compare "redacted@shadowtag-v4.local" vs "redacted@shadowtag-v4.local"
RESULT: They don't match
EVIDENCE: email == stored_email returns False

HYPOTHESIS 2: Emails are not normalized at login
TEST: Check login function
RESULT: Login uses raw email from form
EVIDENCE: login(email=form.email) - no .lower()

ROOT CAUSE FOUND: Login doesn't normalize email, but signup does
```

### Phase 3: VERIFY - Confirm Your Understanding

**Goal:** Prove you understand the root cause.

#### Steps:

1. **Explain the bug in simple terms**
   ```
   "The bug occurs because:
   1. During signup, emails are stored as lowercase
   2. During login, emails are used as-is
   3. String comparison is case-sensitive
   4. Therefore, 'redacted@shadowtag-v4.local' != 'redacted@shadowtag-v4.local'
   ```

2. **Predict the behavior**
   ```
   "If I'm right, then:
   - Logging in with 'redacted@shadowtag-v4.local' will work
   - Logging in with 'redacted@shadowtag-v4.local' will fail
   - Any case variation will fail
   ```

3. **Test your prediction**
   ```python
   def test_email_case_sensitivity():
       create_user(email="redacted@shadowtag-v4.local", password="pass")

       # Predict: lowercase will work (hypothesis)
       result1 = login(email="redacted@shadowtag-v4.local", password="pass")
       assert result1.success is True  # Test prediction

       # Predict: original case will fail (hypothesis)
       result2 = login(email="redacted@shadowtag-v4.local", password="pass")
       assert result2.success is False  # Test prediction
   ```

4. **Understand why it worked before**
   - What changed to cause this?
   - Why didn't we catch it earlier?
   - Are there other places with the same issue?

### Phase 4: FIX - Apply the Correct Solution

**Goal:** Fix the root cause, not the symptom.

#### Steps:

1. **Fix at the root, not the symptom**

   ```python
   # ❌ BAD: Fix the symptom
   def login(email, password):
       # Just handle this one case
       if email == "redacted@shadowtag-v4.local":
           email = "redacted@shadowtag-v4.local"
       # What about other emails?

   # ✅ GOOD: Fix the root cause
   def login(email, password):
       # Normalize email just like signup does
       email = email.lower().strip()
       user = get_user_by_email(email)
       return verify_password(user, password)
   ```

2. **Write a test that verifies the fix**

   ```python
   def test_login_case_insensitive():
       """Login should work regardless of email case"""
       create_user(email="redacted@shadowtag-v4.local", password="pass123")

       # All variations should work
       assert login("redacted@shadowtag-v4.local", "pass123").success is True
       assert login("redacted@shadowtag-v4.local", "pass123").success is True
       assert login("redacted@shadowtag-v4.local", "pass123").success is True
   ```

3. **Verify the fix works**
   - Run the reproduction test - it should pass now
   - Run all related tests
   - Test manually in the actual environment

4. **Prevent recurrence**
   - Add tests for edge cases
   - Document the gotcha
   - Consider architectural improvements
   - Add validation or linting rules

## Complete Example

### Initial Report
```
Bug: User can't log in after signing up
Error: "Invalid credentials"
Happens: Only sometimes, not always
```

### Phase 1: REPRODUCE
```python
# Investigate: When does it fail?
# After testing: Fails when email has uppercase

def test_reproduce_login_bug():
    """Bug: Can't login with uppercase email"""
    create_user(email="redacted@shadowtag-v4.local", password="pass123")
    result = login(email="redacted@shadowtag-v4.local", password="pass123")
    assert result.success is True  # FAILS
```

### Phase 2: ISOLATE
```python
# Check signup
def create_user(email, password):
    user = User(
        email=email.lower(),  # <-- AH! Lowercased here
        password=hash_password(password)
    )
    db.save(user)

# Check login
def login(email, password):
    user = db.get_user_by_email(email)  # <-- NOT lowercased here!
    if not user:
        return LoginResult(success=False, error="Invalid credentials")
    return verify_password(user, password)

# ROOT CAUSE: Signup lowercases email, login doesn't
```

### Phase 3: VERIFY
```python
# Hypothesis: Email stored as lowercase, but searched with original case

# Test 1: Check database
user = db.get_user_by_email("redacted@shadowtag-v4.local")
assert user is not None  # PASSES - lowercase works

# Test 2: Check with uppercase
user = db.get_user_by_email("redacted@shadowtag-v4.local")
assert user is None  # PASSES - uppercase doesn't find it

# HYPOTHESIS CONFIRMED
```

### Phase 4: FIX
```python
# Fix: Normalize email in login too
def login(email, password):
    email = email.lower().strip()  # Match signup normalization
    user = db.get_user_by_email(email)
    if not user:
        return LoginResult(success=False, error="Invalid credentials")
    return verify_password(user, password)

# Test: Verify fix
def test_login_case_insensitive():
    create_user(email="redacted@shadowtag-v4.local", password="pass123")
    assert login("redacted@shadowtag-v4.local", "pass123").success is True
    assert login("redacted@shadowtag-v4.local", "pass123").success is True
    assert login("redacted@shadowtag-v4.local", "pass123").success is True
# ALL PASS ✓

# Prevent: Add helper
def normalize_email(email):
    """Normalize email for consistent storage and comparison"""
    return email.lower().strip()

# Use everywhere:
create_user(email=normalize_email(form.email), ...)
login(email=normalize_email(form.email), ...)
```

## Debugging Tools

### 1. Print/Log Debugging
```python
print(f"DEBUG: variable = {variable}")
logger.debug(f"Function called with: {args}")
```

### 2. Debugger
```python
import pdb; pdb.set_trace()  # Python debugger
# Or use IDE debugger breakpoints
```

### 3. Assertions
```python
assert user is not None, "User should exist at this point"
assert len(items) > 0, f"Expected items, got {items}"
```

### 4. Binary Search (Git Bisect)
```bash
git bisect start
git bisect bad  # Current version has bug
git bisect good v1.2.0  # This version was fine
# Git checks out middle commit - test if bug exists
git bisect bad  # or good
# Repeat until you find the breaking commit
```

## Anti-Patterns to Avoid

### ❌ Random Changes
```python
# DON'T: Try random things hoping something works
# Let me try changing this timeout...
# Maybe if I add await here?
# What if I restart the server?
```

### ❌ Fixing Symptoms
```python
# DON'T: Just handle the error without understanding it
try:
    result = data['user_id']
except KeyError:
    result = None  # Why is user_id missing?
```

### ❌ Changing Multiple Things
```python
# DON'T: Make many changes at once
# "I'll update the library, refactor this function, and change the config"
# Now which change fixed it? Which change broke something else?
```

### ❌ Skipping Reproduction
```python
# DON'T: Skip straight to fixing
# "I think I know what it is, let me just change this..."
# Without a reproduction test, how do you know it's fixed?
```

## Checklist

- [ ] Can you reproduce the bug reliably?
- [ ] Do you have a failing test that demonstrates it?
- [ ] Have you isolated the root cause?
- [ ] Do you understand why it happens?
- [ ] Does your fix address the root cause, not symptoms?
- [ ] Do you have a test that verifies the fix?
- [ ] Have you checked for similar issues elsewhere?
- [ ] Have you prevented this from happening again?

## Remember

1. **REPRODUCE** - Make it happen reliably
2. **ISOLATE** - Find the root cause
3. **VERIFY** - Confirm your understanding
4. **FIX** - Solve the real problem

**Never guess. Always understand.**

Systematic debugging finds problems faster and prevents them from returning.
