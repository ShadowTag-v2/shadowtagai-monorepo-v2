# Defense in Depth

## When to Use

When fixing bugs or implementing features, add multiple layers of protection instead of relying on a single fix. Create robust systems that fail gracefully.

## The Principle

**Single point of failure = fragile system**

Don't rely on one check, one validation, or one fix. Add multiple layers of defense so if one fails, others catch it.

## Layers of Defense

### Layer 1: Input Validation
**Reject bad data before it enters the system**

```python
# ❌ FRAGILE: No input validation
def create_user(email, age):
    user = User(email=email, age=age)
    db.save(user)
    return user

# ✅ ROBUST: Multiple validation layers
def create_user(email: str, age: int) -> User:
    """Create a new user with validated input"""

    # Layer 1: Type validation (via type hints and runtime check)
    if not isinstance(email, str) or not isinstance(age, int):
        raise TypeError("Invalid types for email or age")

    # Layer 2: Format validation
    if not is_valid_email(email):
        raise ValueError(f"Invalid email format: {email}")

    # Layer 3: Business rule validation
    if age < 0 or age > 150:
        raise ValueError(f"Invalid age: {age}")

    # Layer 4: Normalization
    normalized_email = email.lower().strip()

    # Layer 5: Duplicate check
    if user_exists(normalized_email):
        raise DuplicateUserError(f"User already exists: {normalized_email}")

    user = User(email=normalized_email, age=age)
    db.save(user)
    return user
```

### Layer 2: Constraints at Database Level
**Even if application code fails, database enforces rules**

```sql
-- Application validates, but database enforces
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,  -- Database ensures uniqueness
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 150),  -- Database validates age
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(LOWER(email));  -- Case-insensitive lookup
```

### Layer 3: Error Handling
**Handle failures gracefully, don't crash**

```python
# ❌ FRAGILE: Unhandled errors crash the system
def get_user_profile(user_id):
    user = db.get(user_id)  # Could fail
    profile = api.fetch_profile(user.id)  # Could fail
    return profile

# ✅ ROBUST: Multiple error handling layers
def get_user_profile(user_id: int) -> Optional[UserProfile]:
    """Get user profile with graceful error handling"""

    # Layer 1: Input validation
    if not user_id or user_id < 0:
        logger.warning(f"Invalid user_id: {user_id}")
        return None

    # Layer 2: Database error handling
    try:
        user = db.get(user_id)
    except DatabaseError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        return None

    if user is None:
        logger.info(f"User {user_id} not found")
        return None

    # Layer 3: API error handling with retry
    try:
        profile = api.fetch_profile(user.id)
    except APIError as e:
        logger.error(f"API error fetching profile for user {user_id}: {e}")
        # Layer 4: Fallback to cached data
        profile = cache.get(f"profile:{user.id}")
        if profile is None:
            # Layer 5: Return partial data instead of failing
            return UserProfile(user_id=user.id, name=user.name, complete=False)

    return profile
```

### Layer 4: Monitoring and Alerts
**Detect problems before users report them**

```python
# Add monitoring at multiple levels
def process_payment(order_id: int, amount: Decimal) -> PaymentResult:
    """Process payment with comprehensive monitoring"""

    # Layer 1: Log entry point
    logger.info(f"Processing payment", extra={
        'order_id': order_id,
        'amount': amount,
        'trace_id': generate_trace_id()
    })

    # Layer 2: Metrics
    metrics.increment('payments.attempted')
    timer = metrics.timer('payments.duration')

    try:
        # Layer 3: Validate
        if amount <= 0:
            metrics.increment('payments.validation_failed')
            raise ValueError(f"Invalid amount: {amount}")

        # Process payment
        result = payment_gateway.charge(order_id, amount)

        # Layer 4: Verify result
        if result.success:
            metrics.increment('payments.succeeded')
            metrics.record('payments.amount', amount)
        else:
            # Layer 5: Alert on failures
            metrics.increment('payments.failed')
            logger.error(f"Payment failed", extra={
                'order_id': order_id,
                'reason': result.error,
                'trace_id': trace_id
            })
            if result.error_code in CRITICAL_ERRORS:
                alerts.send("Payment gateway critical error", severity="high")

        return result

    except Exception as e:
        # Layer 6: Catch-all error handling
        metrics.increment('payments.error')
        logger.exception(f"Payment processing error: {e}")
        alerts.send(f"Payment exception: {e}", severity="high")
        raise

    finally:
        timer.stop()
```

### Layer 5: Rate Limiting and Throttling
**Protect against abuse and overload**

```python
# ❌ FRAGILE: No protection against abuse
@app.route('/api/send-email', methods=['POST'])
def send_email():
    send_email_to(request.json['recipient'], request.json['message'])
    return {'status': 'sent'}

# ✅ ROBUST: Multiple layers of protection
@app.route('/api/send-email', methods=['POST'])
@require_authentication  # Layer 1: Must be logged in
@rate_limit(max=10, per='minute')  # Layer 2: Max 10 per minute per user
@rate_limit(max=1000, per='hour')  # Layer 3: Max 1000 per hour per user
def send_email():
    # Layer 4: Additional validation
    if not request.json or 'recipient' not in request.json:
        return {'error': 'Invalid request'}, 400

    recipient = request.json['recipient']

    # Layer 5: Validate recipient
    if not is_valid_email(recipient):
        return {'error': 'Invalid recipient email'}, 400

    # Layer 6: Check recipient limits
    if daily_email_count(recipient) > 100:
        return {'error': 'Recipient daily limit exceeded'}, 429

    # Layer 7: Queue instead of immediate send
    email_queue.enqueue(
        recipient=recipient,
        message=request.json['message'],
        sender=current_user.id
    )

    return {'status': 'queued'}
```

### Layer 6: Graceful Degradation
**Keep working even when parts fail**

```python
# ❌ FRAGILE: All-or-nothing approach
def get_dashboard_data(user_id):
    stats = analytics_service.get_stats(user_id)  # If this fails, everything fails
    recommendations = ml_service.get_recommendations(user_id)
    notifications = notification_service.get_notifications(user_id)
    return {
        'stats': stats,
        'recommendations': recommendations,
        'notifications': notifications
    }

# ✅ ROBUST: Graceful degradation
def get_dashboard_data(user_id: int) -> DashboardData:
    """Get dashboard data with graceful degradation"""
    dashboard = DashboardData(user_id=user_id)

    # Layer 1: Try to get stats, fallback to cached/empty
    try:
        dashboard.stats = analytics_service.get_stats(user_id)
    except Exception as e:
        logger.warning(f"Failed to get stats: {e}")
        dashboard.stats = cache.get(f"stats:{user_id}") or default_stats()

    # Layer 2: Try to get recommendations, fallback to popular items
    try:
        dashboard.recommendations = ml_service.get_recommendations(user_id)
    except Exception as e:
        logger.warning(f"Failed to get recommendations: {e}")
        dashboard.recommendations = get_popular_items()

    # Layer 3: Try to get notifications, fallback to empty
    try:
        dashboard.notifications = notification_service.get_notifications(user_id)
    except Exception as e:
        logger.warning(f"Failed to get notifications: {e}")
        dashboard.notifications = []

    # Dashboard still works even if 1-2 services fail!
    return dashboard
```

## Defense in Depth Example: Payment Processing

```python
class PaymentProcessor:
    """Payment processor with defense in depth"""

    def process_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_method: str
    ) -> PaymentResult:
        """
        Process payment with multiple layers of protection:
        1. Input validation
        2. Idempotency checking
        3. Fraud detection
        4. Rate limiting
        5. Error handling
        6. Retry logic
        7. Database transactions
        8. Monitoring and alerts
        """

        # LAYER 1: Input validation
        self._validate_inputs(order_id, amount, payment_method)

        # LAYER 2: Idempotency - prevent duplicate charges
        idempotency_key = f"payment:{order_id}"
        existing = cache.get(idempotency_key)
        if existing:
            logger.info(f"Returning cached result for {order_id}")
            return existing

        # LAYER 3: Fraud detection
        if self._is_fraudulent(order_id, amount):
            self._alert_fraud_team(order_id)
            raise FraudDetectedError("Payment blocked by fraud detection")

        # LAYER 4: Rate limiting
        if not self._check_rate_limit(order_id):
            raise RateLimitError("Too many payment attempts")

        # LAYER 5: Database transaction (atomic)
        with db.transaction():
            # LAYER 6: Lock the order to prevent concurrent processing
            order = db.get_order_with_lock(order_id)

            if order.status == 'paid':
                logger.warning(f"Order {order_id} already paid")
                return PaymentResult(success=True, duplicate=True)

            # LAYER 7: Try payment with retry
            result = self._charge_with_retry(order, amount, payment_method)

            if result.success:
                # LAYER 8: Update order status
                order.status = 'paid'
                order.paid_at = datetime.utcnow()
                db.save(order)

                # LAYER 9: Cache result for idempotency
                cache.set(idempotency_key, result, ttl=3600)

                # LAYER 10: Send confirmation (asynchronously)
                task_queue.enqueue('send_payment_confirmation', order_id)

            else:
                # LAYER 11: Handle failure
                order.status = 'payment_failed'
                order.failure_reason = result.error
                db.save(order)

                # LAYER 12: Alert if critical
                if result.error_code in CRITICAL_ERRORS:
                    alerts.send(f"Critical payment error: {result.error}")

            # LAYER 13: Metrics
            metrics.increment(f'payments.{result.status}')

            return result

    def _charge_with_retry(self, order, amount, payment_method):
        """Retry payment up to 3 times with exponential backoff"""
        for attempt in range(3):
            try:
                return payment_gateway.charge(
                    order_id=order.id,
                    amount=amount,
                    payment_method=payment_method
                )
            except TransientError as e:
                if attempt == 2:  # Last attempt
                    raise
                sleep(2 ** attempt)  # Exponential backoff
                logger.warning(f"Retry payment attempt {attempt + 1}: {e}")

    def _validate_inputs(self, order_id, amount, payment_method):
        """Validate all inputs"""
        if not order_id or order_id <= 0:
            raise ValueError("Invalid order_id")

        if not amount or amount <= 0:
            raise ValueError("Invalid amount")

        if not payment_method or payment_method not in ALLOWED_METHODS:
            raise ValueError("Invalid payment_method")
```

## Benefits

### Single Layer (Fragile)
```python
if user.is_admin:  # Single check
    delete_database()  # Catastrophic if check fails!
```

**Problems:**
- Bug in `is_admin` → disaster
- Database corruption → disaster
- No audit trail → no accountability

### Multiple Layers (Robust)
```python
# Layer 1: Authentication
if not user.is_authenticated:
    raise Unauthorized()

# Layer 2: Authorization
if not user.has_permission('delete_database'):
    raise Forbidden()

# Layer 3: Admin role check
if not user.is_admin:
    raise Forbidden()

# Layer 4: Require confirmation token
if not verify_confirmation_token(request.token):
    raise InvalidToken()

# Layer 5: Audit logging
audit_log.record('database_deletion_attempted', user=user.id)

# Layer 6: Database backup before deletion
backup_database()

# Layer 7: Soft delete first
mark_database_for_deletion()

# Layer 8: Actual deletion after delay
schedule_deletion(delay=24_hours)
```

**Benefits:**
- Multiple checks prevent accidents
- Audit trail shows what happened
- Backup allows recovery
- Delay allows cancellation

## Checklist

When implementing or fixing features:

- [ ] Input validation at API boundary
- [ ] Business rule validation
- [ ] Database constraints
- [ ] Error handling with fallbacks
- [ ] Logging and monitoring
- [ ] Rate limiting where appropriate
- [ ] Graceful degradation
- [ ] Retry logic for transient failures
- [ ] Circuit breakers for failing services
- [ ] Audit logging for critical operations

## Remember

- **One layer = fragile**
- **Multiple layers = robust**
- **Each layer catches what previous layers missed**
- **System works even when some layers fail**

**Don't rely on a single fix. Build defense in depth.**
