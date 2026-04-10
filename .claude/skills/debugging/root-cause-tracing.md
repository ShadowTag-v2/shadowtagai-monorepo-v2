# Root Cause Tracing

## When to Use

When debugging, always trace to the **root cause**, not just the immediate symptom. Use this after you've reproduced a bug to find the real problem.

## The Five Whys Technique

Ask "Why?" repeatedly to drill down from symptom to root cause.

### Example 1: Production Error

```
SYMPTOM: Website is down

Why? → Server returned 500 error
Why? → Database connection failed
Why? → Too many open connections
Why? → Connections not being closed
Why? → Connection pool cleanup code was removed in last refactor

ROOT CAUSE: Connection cleanup removed during refactoring
```

### Example 2: Bug Report

```
SYMPTOM: Users can't upload files

Why? → Upload endpoint returns 413 error
Why? → File size exceeds limit
Why? → Limit set to 1MB
Why? → Default config being used instead of custom config
Why? → Config file not loaded due to typo in filename

ROOT CAUSE: Typo in config filename (config.yaml vs config.yml)
```

## Tracing Strategies

### 1. Backward Tracing - From Error to Source

Start at the error and work backwards to find where it originated.

```python
# Error appears here:
def display_user_profile(user_id):
    user = get_user(user_id)
    return f"Name: {user.name}"  # ❌ AttributeError: 'NoneType' has no attribute 'name'

# Why is user None? Trace backwards...
def get_user(user_id):
    return database.query(User).filter_by(id=user_id).first()  # Returns None

# Why does query return None? Trace backwards...
def filter_by(id):
    return self.where(f"id = {id}")  # ❌ SQL injection! user_id="; DROP TABLE users--"

# Why is user_id malformed? Trace backwards...
def handle_request(request):
    user_id = request.params['user_id']  # ❌ Not validated or sanitized!

# ROOT CAUSE: User input not validated, allowing SQL injection
```

### 2. Forward Tracing - From Input to Error

Start where data enters and trace forward to see where it breaks.

```python
# Input enters here:
def create_order(items):
    print(f"1. Input: {items}")  # [{'id': 1, 'qty': 2}, {'id': 2, 'qty': 1}]

    # Trace forward...
    validated = validate_items(items)
    print(f"2. After validation: {validated}")  # Still a list

    # Continue forward...
    formatted = format_for_db(validated)
    print(f"3. After formatting: {formatted}")  # ❌ Now a string?!

    # Error occurs here:
    total = calculate_total(formatted)  # ❌ Can't iterate over string

# ROOT CAUSE: format_for_db incorrectly returns JSON string instead of dict
```

### 3. Data Flow Tracing

Follow the data through the system to find where it gets corrupted.

```python
# Data flow:
User submits email: "Test@Example.com"
  ↓
Form handler receives: "Test@Example.com"
  ↓
Validation: passes (email looks valid)
  ↓
Signup function: email.lower() → "test@example.com"
  ↓
Database saves: "test@example.com"

# Later, during login:
User submits email: "Test@Example.com"
  ↓
Login function: queries with "Test@Example.com" (❌ not lowercased)
  ↓
Database lookup: no match found
  ↓
Error: "Invalid credentials"

# ROOT CAUSE: Email normalized during signup but not during login
```

## Common Root Cause Patterns

### Pattern 1: Symptom in one place, cause in another

```python
# SYMPTOM: Test fails
def test_calculate_discount():
    result = calculate_discount(100, 0.1)
    assert result == 90  # ❌ FAILS - result is 100

# Immediate cause: No discount applied
def calculate_discount(price, discount_rate):
    discount_amount = price * discount_rate
    return price - discount_amount  # Looks correct!

# But where does discount_rate come from?
def get_discount_rate(user):
    if user.is_premium:
        return 0.1
    return 0  # ❌ Should be returning the discount, not 0

# ROOT CAUSE: get_discount_rate returns 0 for non-premium users
# The bug is not in calculate_discount at all!
```

### Pattern 2: Cascading failures

```python
# SYMPTOM: API returns 500 error

# Immediate error:
def get_user_orders(user_id):
    cache_key = f"orders:{user_id}"
    orders = cache.get(cache_key)  # ❌ Raises RedisConnectionError

# Why did cache fail?
# Redis connection failed

# Why did Redis connection fail?
# Connection timeout

# Why did connection timeout?
# Redis server not responding

# Why is Redis not responding?
# Out of memory

# Why is it out of memory?
# Memory leak in cache code - keys never expire

# ROOT CAUSE: Missing TTL on cached items causes memory leak
```

### Pattern 3: State corruption

```python
# SYMPTOM: Second test fails, first test passes

def test_create_user():
    user = create_user("test@example.com")
    assert user.id == 1  # ✅ PASSES

def test_create_another_user():
    user = create_user("other@example.com")
    assert user.id == 1  # ❌ FAILS - id is 2

# Why is ID different? Trace the state...
# First test creates user with ID 1
# ID counter increments to 2
# First test ends but doesn't clean up database
# Second test starts with dirty state - ID counter still at 2

# ROOT CAUSE: Tests not isolated - shared state between tests
```

## Tracing Tools

### 1. Stack Traces

Read stack traces from bottom to top to trace execution flow:

```
Traceback (most recent call last):
  File "app.py", line 45, in main           ← Started here
    process_orders()
  File "orders.py", line 23, in process_orders  ← Then called this
    total = calculate_total(items)
  File "calc.py", line 10, in calculate_total   ← Which called this
    return sum(item.price for item in items)
  File "calc.py", line 10, in <genexpr>         ← Error happened here
AttributeError: 'dict' has no attribute 'price'
```

Trace: items contains dicts, not objects → Why?

### 2. Logging with Context

Add contextual logging to trace data flow:

```python
def process_payment(order_id, amount):
    logger.info(f"Processing payment", extra={
        'order_id': order_id,
        'amount': amount,
        'trace_id': generate_trace_id()  # Trace through entire request
    })

    user = get_user_for_order(order_id)
    logger.debug(f"Retrieved user", extra={
        'user_id': user.id,
        'trace_id': trace_id
    })

    # Follow the trace_id through all log entries
```

### 3. Debugging with Breakpoints

Use debugger to trace execution step by step:

```python
def problematic_function(data):
    import pdb; pdb.set_trace()  # Pause here

    # Step through line by line
    processed = transform_data(data)
    # Check: What is processed?

    result = calculate(processed)
    # Check: What is result?

    return result
```

### 4. Diff Analysis

Compare working vs broken state:

```bash
# What changed between working version and broken version?
git diff v1.2.0 HEAD -- path/to/file.py

# Or compare configurations
diff config.working.yaml config.broken.yaml
```

## Root Cause vs Symptom

### Symptom: What you observe
```
- Error message
- Test failure
- Unexpected behavior
- Performance issue
```

### Root Cause: Why it happens
```
- Incorrect logic
- Missing validation
- Race condition
- Configuration error
- Resource leak
```

### Example: Don't Fix Symptoms

```python
# SYMPTOM: Division by zero error
def calculate_average(numbers):
    try:
        return sum(numbers) / len(numbers)
    except ZeroDivisionError:
        return 0  # ❌ This hides the real problem!

# ROOT CAUSE: Function called with empty list
# Better fix:
def calculate_average(numbers):
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

# Or at the call site:
if items:
    avg = calculate_average(items)
else:
    # Handle empty case appropriately
```

## Tracing Checklist

- [ ] Have you identified the immediate symptom?
- [ ] Have you traced backwards to the source?
- [ ] Have you asked "Why?" at least 3-5 times?
- [ ] Can you explain the full chain of causation?
- [ ] Have you verified your understanding with evidence?
- [ ] Are you fixing the root cause, not the symptom?
- [ ] Have you checked for similar issues elsewhere?

## Anti-Patterns

### ❌ Stopping at First Cause
```
Error: File not found
Fix: Add try/except to ignore the error
❌ WRONG: Didn't ask WHY the file is missing
```

### ❌ Fixing Symptoms
```
Error: User ID is None
Fix: if user_id is None: user_id = 0
❌ WRONG: Why is it None? Fix the source!
```

### ❌ Adding Workarounds
```
Error: Race condition causes duplicate entries
Fix: Check for duplicates and delete them
❌ WRONG: Fix the race condition, don't clean up after it!
```

## Remember

1. **Symptoms are visible** - errors, failures, wrong behavior
2. **Root causes are hidden** - logic errors, missing validation, wrong assumptions
3. **Always trace to the source** - don't stop at the first explanation
4. **Fix causes, not symptoms** - treating symptoms leaves the problem festering
5. **Verify your understanding** - trace should make complete sense

**The symptom tells you something is wrong.**
**The root cause tells you what to fix.**

Find the root cause, fix it permanently.
