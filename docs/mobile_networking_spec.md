# Mobile Networking Specification — CounselConduit Flutter Client

> Dio Interceptors for Privilege-Preserving Mobile AI
> Version: 1.0 | Target: Flutter 3.32+ / Dart 3.8+

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  Flutter UI  │────▶│ Dio + Intcpt │────▶│ Cloud Run API  │
│  (Material)  │◀────│  (this spec) │◀────│ CounselConduit │
└─────────────┘     └──────────────┘     └────────────────┘
```

## Base Configuration

```dart
final dio = Dio(BaseOptions(
  baseUrl: 'https://counselconduit-767252945109.us-central1.run.app',
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 30),
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Platform': 'flutter',
    'X-Client-Version': appVersion,
  },
));
```

## Interceptor Stack

### 1. Auth Interceptor (Firebase JWT)

```dart
class AuthInterceptor extends Interceptor {
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      final token = await user.getIdToken(true);
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 401) {
      // Token expired — force re-auth
      FirebaseAuth.instance.signOut();
      // Navigate to login
    }
    handler.next(err);
  }
}
```

### 2. Kovel Attestation Interceptor

```dart
class KovelInterceptor extends Interceptor {
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Check for Kovel attestation in response headers
    final attestationId = response.headers.value('X-Kovel-Attestation-Id');
    if (attestationId != null) {
      // Store locally for audit trail
      KovelStore.saveAttestation(attestationId, response.requestOptions.uri);
    }
    handler.next(response);
  }
}
```

### 3. Rate Limit Interceptor

```dart
class RateLimitInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 429) {
      final retryAfter = int.tryParse(
        err.response?.headers.value('Retry-After') ?? '60',
      ) ?? 60;
      // Show user-friendly "slow down" message
      // Queue retry after retryAfter seconds
    }
    handler.next(err);
  }
}
```

### 4. Dead-Man's Switch Interceptor

```dart
class DeadManSwitchInterceptor extends Interceptor {
  Timer? _inactivityTimer;
  static const _timeout = Duration(minutes: 5);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    _resetTimer();
    handler.next(options);
  }

  void _resetTimer() {
    _inactivityTimer?.cancel();
    _inactivityTimer = Timer(_timeout, () {
      // Wipe local session data
      SecureStorage.clearSession();
      // Navigate to lock screen
    });
  }
}
```

### 5. Retry Interceptor

```dart
dio.interceptors.add(RetryInterceptor(
  dio: dio,
  retries: 3,
  retryDelays: const [
    Duration(seconds: 1),
    Duration(seconds: 3),
    Duration(seconds: 5),
  ],
  retryableExtraStatuses: {408, 502, 503, 504},
));
```

## SSE Streaming (Vent Mode)

```dart
Future<void> streamVentResponse(String sessionId, String message) async {
  final response = await dio.post(
    '/vent/stream',
    data: {'session_id': sessionId, 'message': message},
    options: Options(responseType: ResponseType.stream),
  );

  final stream = response.data.stream as Stream<List<int>>;
  await for (final chunk in stream.transform(utf8.decoder)) {
    for (final line in chunk.split('\n')) {
      if (line.startsWith('data: ')) {
        final data = jsonDecode(line.substring(6));
        yield data['content'];
      }
    }
  }
}
```

## Security Requirements

1. **Certificate Pinning**: Pin Cloud Run TLS cert SHA-256
2. **Secure Storage**: Use `flutter_secure_storage` for tokens (Keychain/Keystore)
3. **No Clipboard**: Disable paste for privileged content
4. **Screenshot Protection**: `FLAG_SECURE` on Android, screenshot prevention on iOS
5. **Root/Jailbreak Detection**: Block on compromised devices
6. **No Background Snapshots**: Clear sensitive UI in `AppLifecycleState.paused`

## Dependencies

```yaml
dependencies:
  dio: ^5.8.0
  firebase_auth: ^5.5.0
  flutter_secure_storage: ^9.2.0
  connectivity_plus: ^6.1.0
```
