# Mobile Networking Specification — Flutter/Dio Stack

## Overview

This document specifies the mobile networking architecture for CounselConduit's Flutter client, built on the Dio HTTP client with layered interceptors for auth, privilege enforcement, rate limiting, and dead-man's switch compliance.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  Flutter App                      │
│  ┌────────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ Auth Store  │  │ UI Layer │  │ Offline Q   │  │
│  └──────┬─────┘  └────┬─────┘  └──────┬──────┘  │
│         │             │               │          │
│  ┌──────▼─────────────▼───────────────▼──────┐   │
│  │              Dio HTTP Client               │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │  Interceptor Stack (ordered)        │   │   │
│  │  │  1. AuthInterceptor                 │   │   │
│  │  │  2. KovelPrivilegeInterceptor       │   │   │
│  │  │  3. RateLimitInterceptor            │   │   │
│  │  │  4. DeadManSwitchInterceptor        │   │   │
│  │  │  5. RetryInterceptor                │   │   │
│  │  │  6. LoggingInterceptor              │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  └────────────────────┬──────────────────────┘   │
└───────────────────────┼──────────────────────────┘
                        │ HTTPS
                        ▼
              Cloud Run (CounselConduit API)
```

## Interceptor Specifications

### 1. AuthInterceptor

```dart
class AuthInterceptor extends Interceptor {
  final AuthStore _authStore;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = _authStore.accessToken;
    if (token != null && !_authStore.isExpired) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Attempt silent refresh
      final refreshed = await _authStore.refreshToken();
      if (refreshed) {
        // Retry original request with new token
        final retryResponse = await _retry(err.requestOptions);
        handler.resolve(retryResponse);
        return;
      }
      // Force re-login
      _authStore.logout();
    }
    handler.next(err);
  }
}
```

**Rules:**
- Access tokens: 15–60 min TTL (AGENTS.md Rule 11)
- Refresh tokens: rotate on each use, revocable
- Store tokens in `flutter_secure_storage` (Keychain/Keystore)
- **NEVER** store tokens in SharedPreferences or localStorage

### 2. KovelPrivilegeInterceptor

```dart
class KovelPrivilegeInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Inject Kovel attestation session ID
    options.headers['X-Kovel-Session'] = SessionManager.currentSessionId;
    options.headers['X-Kovel-Firm'] = SessionManager.firmId;
    
    // Strip any client-side system prompt injection attempts (OWASP LLM01)
    if (options.data is Map) {
      (options.data as Map).remove('system_prompt');
      (options.data as Map).remove('system');
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Verify attestation receipt is present in Oracle responses
    if (response.requestOptions.path.contains('/oracle/')) {
      final attestationId = response.data?['attestation_id'];
      if (attestationId == null) {
        // Log compliance warning — attestation missing
        ComplianceLogger.warn('Missing attestation in Oracle response');
      }
    }
    handler.next(response);
  }
}
```

### 3. RateLimitInterceptor

```dart
class RateLimitInterceptor extends Interceptor {
  final _requestCounts = <String, List<DateTime>>{};
  
  // Per-endpoint limits (AGENTS.md Rule 16)
  static const _limits = {
    '/api/oracle/': 10,      // 10 req/min for AI-costly routes
    '/webhooks/': 30,        // 30 req/min for webhooks
    '/api/auth/': 5,         // 5 req/min for auth endpoints
    'default': 60,           // 60 req/min general
  };

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final path = options.path;
    final limit = _getLimitForPath(path);
    
    _requestCounts.putIfAbsent(path, () => []);
    _requestCounts[path]!.removeWhere(
      (t) => DateTime.now().difference(t).inMinutes >= 1,
    );
    
    if (_requestCounts[path]!.length >= limit) {
      handler.reject(DioException(
        requestOptions: options,
        error: 'Client-side rate limit exceeded',
        type: DioExceptionType.cancel,
      ));
      return;
    }
    
    _requestCounts[path]!.add(DateTime.now());
    handler.next(options);
  }
}
```

### 4. DeadManSwitchInterceptor

```dart
class DeadManSwitchInterceptor extends Interceptor {
  Timer? _inactivityTimer;
  static const _timeout = Duration(minutes: 15);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Reset dead-man's switch on any API activity
    _inactivityTimer?.cancel();
    _inactivityTimer = Timer(_timeout, () {
      // Wipe session data
      SessionManager.wipeEphemeral();
      // Force re-auth
      AuthStore.instance.logout();
    });
    handler.next(options);
  }
}
```

### 5. RetryInterceptor

```dart
class RetryInterceptor extends Interceptor {
  static const _maxRetries = 3;
  static const _retryableStatuses = {502, 503, 504};

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final statusCode = err.response?.statusCode;
    if (statusCode != null && _retryableStatuses.contains(statusCode)) {
      final retryCount = err.requestOptions.extra['retryCount'] ?? 0;
      if (retryCount < _maxRetries) {
        await Future.delayed(Duration(seconds: pow(2, retryCount).toInt()));
        err.requestOptions.extra['retryCount'] = retryCount + 1;
        final response = await Dio().fetch(err.requestOptions);
        handler.resolve(response);
        return;
      }
    }
    handler.next(err);
  }
}
```

## API Endpoints

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|------------|
| `/health` | GET | Service health + Firestore | 60/min |
| `/heartbeat` | POST | Session keep-alive | 120/min |
| `/api/auth/token` | POST | JWT exchange | 5/min |
| `/api/auth/refresh` | POST | Token refresh | 10/min |
| `/api/oracle/research` | POST | Oracle Studio pipeline | 10/min |
| `/api/oracle/stream` | POST | SSE Vent Mode | 5/min |
| `/api/transcripts/{id}` | GET | Transcript retrieval | 30/min |
| `/api/export/gdpr` | POST | GDPR data export | 1/hour |
| `/api/billing/portal` | GET | Stripe portal session | 5/min |
| `/webhooks/stripe` | POST | Stripe webhooks | 30/min |

## Error Contract (RFC 9457)

All errors follow the structured `AppError` contract:

```json
{
  "status": 422,
  "code": "VALIDATION_ERROR",
  "message": "Question must be between 10 and 10000 characters",
  "detail": null
}
```

- **Never** expose stack traces (AGENTS.md Rule 5)
- **Never** return raw Firestore documents (AGENTS.md Rule 4)
- All LLM timeouts produce graceful fallback UI (AGENTS.md Rule 25)

## Security Requirements

1. Certificate pinning for production API domain
2. No HTTP fallback — HTTPS only with HSTS preload
3. `flutter_secure_storage` for all token/credential storage
4. Jailbreak/root detection → disable app
5. No screenshot capture allowed in client portal (privilege UX)
6. Screen recording detection → auto-wipe session
7. ProGuard/R8 obfuscation for release builds
8. Binary integrity verification on startup

## Dependencies

```yaml
dependencies:
  dio: ^5.7.0
  flutter_secure_storage: ^9.2.0
  riverpod: ^2.6.0
  freezed_annotation: ^2.4.0
  json_annotation: ^4.9.0
  
dev_dependencies:
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  mockito: ^5.4.0
```
