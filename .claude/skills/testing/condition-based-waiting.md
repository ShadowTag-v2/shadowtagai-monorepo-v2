# Condition-Based Waiting for Tests

## When to Use

When testing asynchronous operations, eventual consistency, or time-dependent behavior. Use polling with conditions instead of arbitrary sleep statements.

## The Problem with Sleep

### ❌ Bad Pattern: Arbitrary Sleep
```python
# WRONG: Guessing how long to wait
def test_async_process():
    start_background_job()
    time.sleep(5)  # Hope 5 seconds is enough?
    assert job_is_complete()
```

**Problems:**
- Tests are **flaky** (pass sometimes, fail sometimes)
- Tests are **slow** (always wait full duration)
- No clear failure reason when timeout
- Brittle when system load varies

## The Solution: Condition-Based Waiting

Wait until a **condition is true**, not for an arbitrary time.

### ✅ Good Pattern: Wait for Condition

```python
def test_async_process():
    start_background_job()

    # Wait until the job is complete, up to 10 seconds
    wait_for(
        condition=lambda: job_is_complete(),
        timeout=10,
        message="Background job did not complete"
    )

    assert job_is_complete()
```

## Core Implementation

### Basic Wait Function

```python
import time
from typing import Callable, Optional

def wait_for(
    condition: Callable[[], bool],
    timeout: float = 10.0,
    poll_interval: float = 0.1,
    message: Optional[str] = None
) -> None:
    """
    Wait until condition returns True, or timeout.

    Args:
        condition: Function that returns True when ready
        timeout: Maximum seconds to wait
        poll_interval: Seconds between checks
        message: Error message if timeout

    Raises:
        TimeoutError: If condition not met within timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(poll_interval)

    error_msg = message or "Condition not met within timeout"
    raise TimeoutError(f"{error_msg} (waited {timeout}s)")
```

### Advanced Wait Function with Better Errors

```python
def wait_for(
    condition: Callable[[], bool],
    timeout: float = 10.0,
    poll_interval: float = 0.1,
    message: Optional[str] = None,
    get_state: Optional[Callable[[], str]] = None
) -> None:
    """
    Wait with detailed error reporting.

    Args:
        get_state: Optional function to get current state for error messages
    """
    start_time = time.time()
    last_exception = None

    while time.time() - start_time < timeout:
        try:
            if condition():
                return
        except Exception as e:
            last_exception = e

        time.sleep(poll_interval)

    # Build detailed error message
    elapsed = time.time() - start_time
    error_msg = message or "Condition not met"

    if get_state:
        current_state = get_state()
        error_msg += f"\nCurrent state: {current_state}"

    if last_exception:
        error_msg += f"\nLast exception: {last_exception}"

    raise TimeoutError(f"{error_msg} (waited {elapsed:.1f}s)")
```

## Common Patterns

### 1. Waiting for Element to Appear

```python
def test_modal_appears_after_click():
    click_button("Open Modal")

    wait_for(
        condition=lambda: modal_is_visible(),
        timeout=5,
        message="Modal did not appear after clicking button"
    )

    assert get_modal_title() == "Welcome"
```

### 2. Waiting for State Change

```python
def test_order_processing():
    order_id = create_order(items=["item1", "item2"])

    wait_for(
        condition=lambda: get_order_status(order_id) == "completed",
        timeout=30,
        message=f"Order {order_id} did not complete",
        get_state=lambda: f"Order status: {get_order_status(order_id)}"
    )

    order = get_order(order_id)
    assert order.status == "completed"
```

### 3. Waiting for API Response

```python
def test_webhook_processed():
    send_webhook(url="/webhook", data={"event": "user.created"})

    def webhook_processed():
        events = get_processed_events()
        return any(e.type == "user.created" for e in events)

    wait_for(
        condition=webhook_processed,
        timeout=15,
        message="Webhook event was not processed"
    )
```

### 4. Waiting for File Creation

```python
def test_export_creates_file():
    export_id = start_export(format="csv")
    file_path = f"/exports/{export_id}.csv"

    wait_for(
        condition=lambda: os.path.exists(file_path),
        timeout=20,
        message=f"Export file not created: {file_path}"
    )

    assert os.path.getsize(file_path) > 0
```

### 5. Waiting for Database Record

```python
def test_user_created_in_database():
    create_user_async(email="test@example.com")

    def user_exists():
        user = db.query(User).filter_by(email="test@example.com").first()
        return user is not None

    wait_for(
        condition=user_exists,
        timeout=10,
        message="User not created in database"
    )
```

### 6. Waiting for Multiple Conditions

```python
def test_job_completes_successfully():
    job_id = start_job()

    def job_done_successfully():
        job = get_job(job_id)
        return job.status == "completed" and job.error is None

    wait_for(
        condition=job_done_successfully,
        timeout=60,
        message=f"Job {job_id} did not complete successfully",
        get_state=lambda: f"Job: {get_job(job_id)}"
    )
```

## Framework-Specific Implementations

### Pytest Fixture

```python
import pytest

@pytest.fixture
def wait_for():
    """Provide wait_for helper to all tests"""
    def _wait_for(condition, timeout=10, message=None):
        start = time.time()
        while time.time() - start < timeout:
            if condition():
                return
            time.sleep(0.1)
        raise TimeoutError(message or "Timeout waiting for condition")
    return _wait_for

def test_with_waiting(wait_for):
    start_process()
    wait_for(lambda: process_is_done(), timeout=5)
```

### Async Version

```python
import asyncio

async def wait_for_async(
    condition: Callable[[], bool],
    timeout: float = 10.0,
    poll_interval: float = 0.1,
    message: Optional[str] = None
) -> None:
    """Async version of wait_for"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        if await condition():
            return
        await asyncio.sleep(poll_interval)

    raise TimeoutError(message or f"Timeout after {timeout}s")

# Usage
async def test_async_operation():
    await start_async_job()

    await wait_for_async(
        condition=lambda: check_job_complete(),
        timeout=15
    )
```

## Best Practices

### 1. Choose Appropriate Timeouts
```python
# Quick operations: 1-5 seconds
wait_for(condition=lambda: cache_updated(), timeout=2)

# Network operations: 10-30 seconds
wait_for(condition=lambda: api_responds(), timeout=15)

# Heavy processing: 30-120 seconds
wait_for(condition=lambda: report_generated(), timeout=60)
```

### 2. Use Descriptive Error Messages
```python
# ❌ Bad: Generic message
wait_for(lambda: user_exists(), timeout=5)

# ✅ Good: Specific context
wait_for(
    lambda: user_exists(),
    timeout=5,
    message=f"User {email} was not created in database after registration"
)
```

### 3. Provide State Information
```python
wait_for(
    condition=lambda: get_status() == "ready",
    message="Service did not become ready",
    get_state=lambda: f"Current status: {get_status()}, uptime: {get_uptime()}s"
)
```

### 4. Adjust Poll Intervals
```python
# Fast polling for quick operations (100ms)
wait_for(condition, poll_interval=0.1)

# Slower polling for expensive checks (1s)
wait_for(
    condition=lambda: database_migration_complete(),
    poll_interval=1.0,
    timeout=300
)
```

## Anti-Patterns

### ❌ Using Sleep Instead of Wait
```python
# WRONG
def test_job_completes():
    start_job()
    time.sleep(10)  # Arbitrary wait
    assert job_is_done()
```

### ❌ Polling Too Frequently
```python
# WRONG: Checking every 1ms is wasteful
wait_for(condition, poll_interval=0.001, timeout=60)
```

### ❌ Not Handling Exceptions in Condition
```python
# WRONG: Condition might raise exception
wait_for(lambda: db.get_record(id).status == "done")

# RIGHT: Handle potential exceptions
wait_for(lambda: (r := db.get_record(id)) and r.status == "done")
```

## Benefits

1. **Reliable** - Tests pass consistently
2. **Fast** - Only wait as long as needed
3. **Clear Failures** - Know exactly what timed out
4. **Maintainable** - Easy to adjust timeouts
5. **Realistic** - Tests match actual async behavior

## Remember

- **Never use arbitrary sleep** in tests
- **Always wait for conditions** to be true
- **Provide clear timeout messages**
- **Choose appropriate timeouts** for the operation
- **Poll at reasonable intervals**

Condition-based waiting makes tests reliable, fast, and maintainable.
