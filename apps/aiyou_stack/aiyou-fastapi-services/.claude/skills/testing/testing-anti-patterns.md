# Testing Anti-Patterns

## When to Use

Reference this when writing or reviewing tests to avoid common pitfalls that make tests fragile, slow, or unmaintainable.

## Anti-Pattern Categories

### 1. Test Structure Anti-Patterns

#### ❌ The Liar
Test passes but doesn't actually verify the behavior.

```python
# BAD: Test claims to verify but doesn't
def test_user_creation():
    create_user("redacted@shadowtag-v4.local", "password")
    # No assertions! Test always passes

# BAD: Meaningless assertion
def test_calculate_total():
    result = calculate_total([10, 20, 30])
    assert result is not None  # Doesn't verify correctness
```

**Fix:**
```python
# GOOD: Actually verifies behavior
def test_user_creation():
    user = create_user("redacted@shadowtag-v4.local", "password")
    assert user.id is not None
    assert user.email == "redacted@shadowtag-v4.local"

def test_calculate_total():
    result = calculate_total([10, 20, 30])
    assert result == 60  # Verifies correct calculation
```

#### ❌ The Giant
One test that tests everything.

```python
# BAD: Massive test testing entire system
def test_entire_user_workflow():
    # Create user
    user = create_user("redacted@shadowtag-v4.local", "pass")
    # Login
    token = login(user.email, "pass")
    # Update profile
    update_profile(user.id, name="New Name")
    # Create post
    post = create_post(user.id, "Hello")
    # Comment on post
    comment = add_comment(post.id, "Nice!")
    # Delete everything
    # ... 100 more lines
```

**Fix:**
```python
# GOOD: Separate focused tests
def test_create_user():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    assert user.id is not None

def test_login_with_valid_credentials():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    token = login(user.email, "pass")
    assert token is not None

def test_update_user_profile():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    updated = update_profile(user.id, name="New Name")
    assert updated.name == "New Name"
```

#### ❌ The Mockery
Everything is mocked, nothing is actually tested.

```python
# BAD: Mocking the entire system
def test_process_payment(mocker):
    mocker.patch('payment_service.validate_card', return_value=True)
    mocker.patch('payment_service.charge_card', return_value={'success': True})
    mocker.patch('payment_service.send_receipt', return_value=True)
    mocker.patch('database.save_transaction', return_value=True)

    result = process_payment(card_info, amount)
    assert result is True  # But did anything actually work?
```

**Fix:**
```python
# GOOD: Mock only external dependencies
def test_process_payment():
    # Use real payment service logic
    # Mock only external payment gateway
    with mock_payment_gateway(success=True):
        result = process_payment(card_info, amount=100)
        assert result.success is True
        assert result.amount == 100

    # Verify transaction saved to test database
    transaction = db.get_transaction(result.transaction_id)
    assert transaction.amount == 100
```

### 2. Timing Anti-Patterns

#### ❌ The Sleeper
Uses arbitrary sleep instead of condition-based waiting.

```python
# BAD: Arbitrary sleep
def test_async_job():
    start_job()
    time.sleep(5)  # Hope it's done?
    assert job_is_complete()
```

**Fix:**
```python
# GOOD: Wait for condition
def test_async_job():
    start_job()
    wait_for(
        condition=lambda: job_is_complete(),
        timeout=10,
        message="Job did not complete"
    )
    assert job_is_complete()
```

#### ❌ The Flicker
Test passes and fails randomly due to timing issues.

```python
# BAD: Race condition
def test_concurrent_updates():
    update_counter()  # Async
    update_counter()  # Async
    assert get_counter() == 2  # Sometimes 1, sometimes 2
```

**Fix:**
```python
# GOOD: Synchronize properly
def test_concurrent_updates():
    futures = [
        async_update_counter(),
        async_update_counter()
    ]
    wait_all(futures)
    assert get_counter() == 2
```

### 3. Dependency Anti-Patterns

#### ❌ The Chain Gang
Tests depend on each other running in order.

```python
# BAD: Tests coupled together
class TestUserLifecycle:
    user_id = None

    def test_1_create_user(self):
        user = create_user("redacted@shadowtag-v4.local")
        TestUserLifecycle.user_id = user.id  # State shared!

    def test_2_update_user(self):
        # Depends on test_1 running first
        update_user(TestUserLifecycle.user_id, name="New")

    def test_3_delete_user(self):
        # Depends on test_1 and test_2
        delete_user(TestUserLifecycle.user_id)
```

**Fix:**
```python
# GOOD: Independent tests
class TestUserLifecycle:
    @pytest.fixture
    def user(self):
        return create_user("redacted@shadowtag-v4.local")

    def test_create_user(self):
        user = create_user("redacted@shadowtag-v4.local")
        assert user.id is not None

    def test_update_user(self, user):
        updated = update_user(user.id, name="New")
        assert updated.name == "New"

    def test_delete_user(self, user):
        delete_user(user.id)
        assert get_user(user.id) is None
```

#### ❌ The Contaminator
Test modifies shared state and doesn't clean up.

```python
# BAD: Leaves database dirty
def test_create_user():
    user = create_user("redacted@shadowtag-v4.local")
    assert user.id is not None
    # No cleanup! Affects other tests
```

**Fix:**
```python
# GOOD: Cleanup after test
def test_create_user():
    user = create_user("redacted@shadowtag-v4.local")
    assert user.id is not None
    try:
        # Test assertions
        assert user.email == "redacted@shadowtag-v4.local"
    finally:
        # Always cleanup
        delete_user(user.id)

# BETTER: Use fixture with cleanup
@pytest.fixture
def user():
    user = create_user("redacted@shadowtag-v4.local")
    yield user
    delete_user(user.id)

def test_create_user(user):
    assert user.id is not None
```

### 4. Assertion Anti-Patterns

#### ❌ The Generalist
Vague assertions that don't verify specific behavior.

```python
# BAD: Too general
def test_get_user():
    user = get_user(123)
    assert user  # Just checks truthy
    assert len(user.__dict__) > 0  # Meaningless

# BAD: String matching too loose
def test_error_message():
    with pytest.raises(Exception):  # Any exception?
        risky_operation()
```

**Fix:**
```python
# GOOD: Specific assertions
def test_get_user():
    user = get_user(123)
    assert user.id == 123
    assert user.email == "redacted@shadowtag-v4.local"
    assert user.is_active is True

# GOOD: Specific exception and message
def test_error_message():
    with pytest.raises(ValueError, match="User ID must be positive"):
        get_user(-1)
```

#### ❌ The Examiner
Too many assertions in one test.

```python
# BAD: Testing multiple behaviors
def test_user_operations():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    assert user.id is not None
    assert user.email == "redacted@shadowtag-v4.local"

    logged_in = login(user.email, "pass")
    assert logged_in is True

    updated = update_profile(user.id, name="New")
    assert updated.name == "New"
    # If any assertion fails, we don't know which behavior broke
```

**Fix:**
```python
# GOOD: One behavior per test
def test_create_user_returns_valid_user():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    assert user.id is not None
    assert user.email == "redacted@shadowtag-v4.local"

def test_login_with_valid_credentials_succeeds():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    logged_in = login(user.email, "pass")
    assert logged_in is True

def test_update_profile_changes_name():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    updated = update_profile(user.id, name="New")
    assert updated.name == "New"
```

### 5. Scope Anti-Patterns

#### ❌ The Inspector
Tests implementation details instead of behavior.

```python
# BAD: Testing internal structure
def test_user_password_storage():
    user = create_user("redacted@shadowtag-v4.local", "password123")
    assert hasattr(user, '_password_hash')
    assert user._password_hash.startswith('$2b$')
    assert user._salt is not None

# BAD: Testing private methods
def test_internal_validation():
    result = user_service._validate_email_format("redacted@shadowtag-v4.local")
    assert result is True
```

**Fix:**
```python
# GOOD: Test public behavior
def test_user_can_login_with_correct_password():
    create_user("redacted@shadowtag-v4.local", "password123")
    user = login("redacted@shadowtag-v4.local", "password123")
    assert user is not None

def test_create_user_with_invalid_email_fails():
    with pytest.raises(ValueError, match="Invalid email"):
        create_user("not-an-email", "password123")
```

#### ❌ The Nitpicker
Tests framework or library code instead of your code.

```python
# BAD: Testing that Python/libraries work
def test_list_append():
    items = []
    items.append(1)
    assert len(items) == 1  # Testing Python, not your code

def test_database_connection():
    conn = database.connect()
    assert conn is not None  # Testing database library
```

**Fix:**
```python
# GOOD: Test your actual business logic
def test_add_item_to_shopping_cart():
    cart = ShoppingCart()
    cart.add_item(product_id=123, quantity=2)
    assert cart.total_items() == 2
    assert cart.get_item(123).quantity == 2

def test_save_user_persists_to_database():
    user = User(email="redacted@shadowtag-v4.local")
    save_user(user)

    retrieved = get_user_by_email("redacted@shadowtag-v4.local")
    assert retrieved.email == user.email
```

### 6. Performance Anti-Patterns

#### ❌ The Slow Poke
Tests take forever to run.

```python
# BAD: Slow integration test for unit-testable code
def test_calculate_discount():
    # Starts entire application, database, etc.
    app = start_full_application()
    response = app.post('/api/calculate-discount', json={
        'price': 100,
        'discount_percent': 10
    })
    assert response.json()['final_price'] == 90
    # Takes 5 seconds for simple calculation!
```

**Fix:**
```python
# GOOD: Fast unit test
def test_calculate_discount():
    result = calculate_discount(price=100, discount_percent=10)
    assert result == 90
    # Takes 0.001 seconds
```

#### ❌ The Database Hog
Every test hits a real database.

```python
# BAD: All tests use real database
def test_user_validation():
    db.connect()
    user = db.create_user("redacted@shadowtag-v4.local")
    result = validate_user(user)
    db.cleanup()
    # Slow, fragile, requires database
```

**Fix:**
```python
# GOOD: Unit test with in-memory data
def test_user_validation():
    user = User(email="redacted@shadowtag-v4.local", age=25)
    result = validate_user(user)
    assert result.is_valid is True

# Or use in-memory database for integration tests
@pytest.fixture
def db():
    return InMemoryDatabase()
```

### 7. Naming Anti-Patterns

#### ❌ The Mystery Guest
Test names don't describe what they test.

```python
# BAD: Unclear names
def test_1():
    ...

def test_user():
    ...

def test_edge_case():
    ...
```

**Fix:**
```python
# GOOD: Descriptive names
def test_create_user_with_valid_email_succeeds():
    ...

def test_login_with_wrong_password_fails():
    ...

def test_calculate_total_with_empty_cart_returns_zero():
    ...
```

## Red Flags

Watch for these warning signs:

1. Tests take > 1 second to run
2. Tests fail randomly
3. Tests fail when run in different order
4. Tests require specific setup steps
5. Test failures don't clearly indicate what broke
6. Tests break when refactoring (but behavior unchanged)
7. Multiple tests break when one thing changes
8. Tests require commenting out to pass
9. Tests use `time.sleep()`
10. Tests mock everything

## Quick Reference

| Anti-Pattern | Red Flag | Fix |
|--------------|----------|-----|
| The Liar | No assertions or weak assertions | Assert specific behavior |
| The Giant | 100+ line tests | One behavior per test |
| The Mockery | Mocking everything | Mock only external deps |
| The Sleeper | `time.sleep()` in tests | Use condition-based waiting |
| The Chain Gang | Tests depend on each other | Independent tests with fixtures |
| The Inspector | Testing private methods | Test public behavior |
| The Slow Poke | Tests take minutes | Unit tests in milliseconds |

## Remember

- **Test behavior, not implementation**
- **One test, one thing**
- **Fast tests, run often**
- **Independent tests, any order**
- **Clear failures, easy debugging**

Avoid these anti-patterns to create maintainable, reliable test suites.
