# Test-Driven Development (TDD)

## When to Use

**ALWAYS** when implementing new features, fixing bugs, or refactoring code. TDD is mandatory, not optional.

## The RED-GREEN-REFACTOR Cycle

### Phase 1: RED - Write a Failing Test

1. **Write the test FIRST** before any implementation code
2. The test must **fail** for the right reason (feature not implemented)
3. Test should be clear, readable, and test ONE thing

**Example:**
```python
def test_user_can_create_account():
    """User should be able to create a new account with email and password"""
    user = create_user(email="redacted@shadowtag-v4.local", password="[VAPORIZED_PWD]")
    assert user.id is not None
    assert user.email == "redacted@shadowtag-v4.local"
    assert user.is_active is True
```

**Run the test** - it should fail with a clear message like:
```
NameError: name 'create_user' is not defined
```

### Phase 2: GREEN - Make It Pass

1. Write the **minimal** code to make the test pass
2. Don't worry about perfection - just make it work
3. Don't add extra features or "nice to haves"

**Example:**
```python
def create_user(email: str, password: str) -> User:
    user = User(
        id=generate_id(),
        email=email,
        is_active=True
    )
    db.save(user)
    return user
```

**Run the test again** - it should pass:
```
test_user_can_create_account ... PASSED
```

### Phase 3: REFACTOR - Improve the Code

1. Now improve the code quality
2. Remove duplication
3. Improve naming and structure
4. Add error handling
5. **Tests must still pass** after each refactoring

**Example:**
```python
def create_user(email: str, password: str) -> User:
    """Create a new user account with the given credentials"""
    if not email or not password:
        raise ValueError("Email and password are required")

    if not is_valid_email(email):
        raise ValueError("Invalid email format")

    hashed_password = hash_password(password)

    user = User(
        id=generate_id(),
        email=email.lower(),
        password_hash=hashed_password,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.save(user)
    return user
```

**Run tests** - should still pass after refactoring.

## Key Principles

### 1. Tests Come First
- **NEVER** write implementation code before the test
- The test defines what "done" looks like
- Forces you to think about API design

### 2. One Test, One Thing
- Each test verifies a single behavior
- Clear test names describe what they test
- Easy to understand what failed when it fails

### 3. Test Behavior, Not Implementation
```python
# ❌ BAD - Tests implementation details
def test_user_stored_in_dictionary():
    create_user("redacted@shadowtag-v4.local", "pass")
    assert "redacted@shadowtag-v4.local" in users_dict

# ✅ GOOD - Tests behavior
def test_user_can_be_retrieved_after_creation():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    found = get_user_by_email("redacted@shadowtag-v4.local")
    assert found.id == user.id
```

### 4. Keep Tests Fast
- Unit tests should run in milliseconds
- Use mocks for external dependencies
- Database tests use in-memory or test databases

### 5. Test Naming Convention
Use descriptive names that explain the scenario:

```python
test_<action>_<condition>_<expected_result>

# Examples:
test_create_user_with_valid_email_succeeds()
test_create_user_with_invalid_email_raises_error()
test_get_user_when_not_exists_returns_none()
```

## Workflow

```
1. Write failing test (RED)
   ↓
2. Run test - verify it fails correctly
   ↓
3. Write minimal code (GREEN)
   ↓
4. Run test - verify it passes
   ↓
5. Refactor code (REFACTOR)
   ↓
6. Run test - verify still passes
   ↓
7. Repeat for next feature
```

## TDD for Bug Fixes

When fixing a bug:

1. **Write a test that reproduces the bug** (RED)
2. Verify the test fails
3. Fix the bug (GREEN)
4. Verify the test passes
5. Refactor if needed (REFACTOR)

**Example:**
```python
def test_login_with_mixed_case_email_succeeds():
    """Bug: Login fails when email case doesn't match exactly"""
    create_user("redacted@shadowtag-v4.local", "password123")

    # Should work with any case variation
    user = login("redacted@shadowtag-v4.local", "password123")
    assert user is not None
```

## Common Patterns

### Testing Error Cases

```python
def test_create_user_without_email_raises_error():
    with pytest.raises(ValueError, match="Email.*required"):
        create_user(email="", password="pass123")

def test_create_user_with_short_password_raises_error():
    with pytest.raises(ValueError, match="Password.*8 characters"):
        create_user(email="redacted@shadowtag-v4.local", password="123")
```

### Testing Async Code

```python
async def test_fetch_user_data_returns_user_info():
    user = await fetch_user_data(user_id=123)
    assert user.name == "John Doe"
    assert user.email == "redacted@shadowtag-v4.local"
```

### Using Fixtures

```python
@pytest.fixture
def sample_user():
    """Provide a test user for tests"""
    return create_user("redacted@shadowtag-v4.local", "password123")

def test_user_can_update_profile(sample_user):
    updated = update_user_profile(sample_user.id, name="New Name")
    assert updated.name == "New Name"
```

## Anti-Patterns to Avoid

### ❌ Writing Implementation First
```python
# WRONG: Writing the function first
def create_user(email, password):
    # ... implementation

# Then writing test after
def test_create_user():
    # ...
```

### ❌ Skipping the RED Phase
```python
# WRONG: Test passes immediately (not testing anything useful)
def test_create_user():
    result = create_user("redacted@shadowtag-v4.local", "pass")
    assert result is not None  # This would pass even if broken
```

### ❌ Testing Multiple Things
```python
# WRONG: One test doing too much
def test_user_operations():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    login(user.email, "pass")
    update_profile(user.id, name="New")
    delete_user(user.id)
    # Too many concerns in one test
```

### ❌ Testing Implementation Details
```python
# WRONG: Test knows too much about internals
def test_user_password_hashing():
    user = create_user("redacted@shadowtag-v4.local", "pass")
    assert user._password_hash.startswith("$2b$")  # Coupled to bcrypt
```

## Benefits

1. **Confidence** - Tests prove your code works
2. **Design** - Tests force good API design
3. **Documentation** - Tests show how to use the code
4. **Regression Prevention** - Tests catch future breaks
5. **Refactoring Safety** - Change code fearlessly

## Remember

- **RED**: Write a failing test first
- **GREEN**: Make it pass with minimal code
- **REFACTOR**: Clean up while keeping tests green
- **REPEAT**: Every feature, every bug fix

TDD is not optional. It's the foundation of quality software development.
