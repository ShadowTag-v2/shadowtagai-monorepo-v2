// flutter/lib/network/omega_dio_client.dart
//
// Omega Dio Client — Flutter Edge Network Layer
//
// The Dart edge intercepts Judge 6.1 terminal events natively.
// Every request is stamped with tenant identity and model lock.
// Every response is inspected for J-6 enforcement signals:
//   402 → Wet Fleece (payment required)
//   406 → Kickback (unauthorized practice detected)
//   423 → Locked (RKILL executed)
//
// v4.2 additions:
//   - 401 token-refresh interceptor (single retry with fresh token)
//   - authorizeBackbrief exponential backoff retry (3 attempts)
//   - dispatchOpord now uses _retryablePost for consistency
//   - retryable POST helper for all idempotent endpoints

import 'dart:developer' show log;
import 'dart:math' show min;

import 'package:dio/dio.dart';

/// Async callback to obtain a fresh auth token.
///
/// Called by the 401-interceptor when the server rejects the current token.
/// Implementations should contact the auth provider (Firebase Auth, etc.)
/// and return a new bearer token string. Return `null` to skip retry.
typedef TokenProvider = Future<String?> Function();

/// Exception thrown when Judge 6.1 enforces a terminal policy.
///
/// Maps J-6 enforcement signals into structured Dart exceptions:
/// - 402 → `PAYMENT_REQUIRED` (Wet Fleece)
/// - 406 → `KICKBACK` (unauthorized practice detected)
/// - 423 → `RKILL` (locked)
class JudgeSixException implements Exception {
  /// The enforcement status (RKILL, KICKBACK, PAYMENT_REQUIRED).
  final String status;

  /// The reason code explaining the enforcement.
  final String reasonCode;

  /// Human-readable explanation.
  final String reason;

  JudgeSixException(this.status, this.reasonCode, [this.reason = '']);

  @override
  String toString() => 'JudgeSixException($status: $reasonCode - $reason)';
}

/// Omega Dio Client — Zero Trust network layer for Flutter.
///
/// Every request is authenticated with tenant identity.
/// Every response is inspected for J-6 enforcement.
/// The model is locked to prevent unauthorized model switching.
///
/// v4.1: Supports automatic 401 token refresh via [tokenProvider] and
/// exponential backoff retries on transient failures.
class OmegaDioClient {
  /// The underlying Dio instance.
  final Dio dio;

  /// The tenant identifier.
  final String tenantId;

  /// Optional async callback to refresh an expired auth token.
  ///
  /// When provided, 401 responses trigger a single retry: the interceptor
  /// calls [tokenProvider], updates the `Authorization` header, and replays
  /// the original request exactly once.
  final TokenProvider? tokenProvider;

  /// Maximum retry attempts for retryable endpoints (e.g. backbrief).
  static const int _maxRetries = 3;

  /// Base delay for exponential backoff (doubles per attempt).
  static const Duration _baseDelay = Duration(milliseconds: 500);

  /// Creates an OmegaDioClient with ZTA interceptors.
  ///
  /// [baseUrl] - The API base URL (Cor.Go ZTA kernel).
  /// [tenantId] - The authenticated tenant identifier.
  /// [modelLock] - The locked model identifier (immutable).
  /// [tokenProvider] - Optional callback to refresh expired bearer tokens.
  OmegaDioClient({
    required String baseUrl,
    required this.tenantId,
    String modelLock = 'gemini-3.1-flash-lite-preview-thinking',
    this.tokenProvider,
  }) : dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 35), // UCMJ Article 92 timeout
    headers: {
      'Content-Type': 'application/json',
    },
    // Route 4xx responses through onResponse so J-6 interceptor can inspect them.
    // Without this, Dio defaults to 200-299 only, sending 402/406/423 straight
    // to onError and completely bypassing the enforcement logic.
    validateStatus: (status) => status != null && status < 500,
  )) {
    // Request interceptor: stamp every request with ZTA metadata
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        options.headers['X-Tenant-Id'] = tenantId;
        options.headers['X-Model-Lock'] = modelLock;
        options.headers['X-Client'] = 'omega-dio-flutter';
        return handler.next(options);
      },
    ));

    // Response interceptor: intercept J-6 terminal events + 401 token refresh
    dio.interceptors.add(InterceptorsWrapper(
      onResponse: (response, handler) async {
        final statusCode = response.statusCode ?? 200;
        final data = response.data;

        // ── 401 Token Refresh ──
        // If the server rejects our token and we have a provider, refresh once.
        if (statusCode == 401 && tokenProvider != null) {
          // Guard against infinite retry loops: only attempt once per request.
          if (response.requestOptions.extra['_tokenRetried'] == true) {
            log('🔒 401 token refresh already attempted — not retrying');
            return handler.next(response);
          }

          log('🔄 401 received — attempting token refresh');
          try {
            final newToken = await tokenProvider!();
            if (newToken != null && newToken.isNotEmpty) {
              // Clone the original request with the fresh token
              final opts = response.requestOptions;
              opts.headers['Authorization'] = 'Bearer $newToken';
              opts.extra['_tokenRetried'] = true;

              final retryResponse = await dio.fetch(opts);
              return handler.resolve(retryResponse);
            }
          } catch (refreshError) {
            log('⚠️ Token refresh failed: $refreshError');
          }
          // Fall through to normal handling if refresh fails
          return handler.next(response);
        }

        // ── J-6 Enforcement ──
        if (statusCode == 402 || statusCode == 406 || statusCode == 423) {
          final status = data is Map ? (data['status'] ?? 'UNKNOWN') : 'UNKNOWN';
          final reasonCode = data is Map ? (data['reason_code'] ?? 'Blocked') : 'Blocked';
          final reason = data is Map ? (data['reason'] ?? '') : '';

          return handler.reject(DioException(
            requestOptions: response.requestOptions,
            response: response,
            error: JudgeSixException(status, reasonCode, reason),
            type: DioExceptionType.badResponse,
          ));
        }

        return handler.next(response);
      },
      onError: (error, handler) {
        // Log J-6 enforcement for observability
        if (error.error is JudgeSixException) {
          final j6 = error.error as JudgeSixException;
          log('⚖️ Judge 6.1 Enforcement: ${j6.status} - ${j6.reasonCode}');
        }
        return handler.next(error);
      },
    ));
  }

  /// Dispatch an OPORD to the ZTA kernel with retry on transient failures.
  ///
  /// Returns the workflow ID on success, or an empty string if absent.
  /// Retries up to [_maxRetries] times on 5xx/timeout errors.
  /// Throws [DioException] wrapping [JudgeSixException] on J-6 enforcement.
  Future<String> dispatchOpord({
    required String payload,
    required String hash,
    String agentId = 'Architect',
  }) async {
    final response = await _retryablePost(
      '/api/v5/zta/evaluate',
      data: {
        'tenant_id': tenantId,
        'payload': payload,
        'hash': hash,
        'agent_id': agentId,
      },
      operationName: 'dispatchOpord',
    );

    final data = response.data;
    if (data is Map) {
      return (data['workflow_id'] as String?) ?? '';
    }
    return '';
  }

  /// Send a backbrief authorization signal with exponential backoff retry.
  ///
  /// Retries up to [_maxRetries] times on transient failures (5xx, timeouts,
  /// connection errors). J-6 enforcement errors (402/406/423) are NOT retried
  /// as they represent terminal policy decisions.
  ///
  /// Backoff schedule: 500ms → 1s → 2s (capped at 4s).
  Future<void> authorizeBackbrief(bool authorized) async {
    await _retryablePost(
      '/api/v5/temporal/signal_backbrief',
      data: {'authorized': authorized},
      operationName: 'authorizeBackbrief',
    );
  }

  /// Generic retryable POST with exponential backoff.
  ///
  /// Only retries on transient errors:
  /// - 5xx server errors
  /// - Connection timeouts
  /// - Send/receive timeouts
  ///
  /// Does NOT retry on:
  /// - 4xx client errors (including J-6 enforcement)
  /// - Successful responses
  Future<Response> _retryablePost(
    String path, {
    required Map<String, dynamic> data,
    required String operationName,
    int maxRetries = _maxRetries,
  }) async {
    DioException? lastError;

    for (int attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        final response = await dio.post(path, data: data);
        final statusCode = response.statusCode ?? 200;

        // Success — return immediately
        if (statusCode >= 200 && statusCode < 300) {
          if (attempt > 0) {
            log('✅ $operationName succeeded on attempt ${attempt + 1}');
          }
          return response;
        }

        // 5xx — retryable server error
        if (statusCode >= 500 && attempt < maxRetries) {
          final delay = _backoffDelay(attempt);
          log('⚠️ $operationName returned $statusCode — '
              'retrying in ${delay.inMilliseconds}ms '
              '(attempt ${attempt + 1}/$maxRetries)');
          await Future<void>.delayed(delay);
          continue;
        }

        // Non-retryable status code — return as-is (J-6 interceptor handles 4xx)
        return response;
      } on DioException catch (e) {
        lastError = e;

        // J-6 enforcement errors are terminal — do not retry
        if (e.error is JudgeSixException) {
          rethrow;
        }

        // Only retry on transient network/timeout errors
        final retryable = e.type == DioExceptionType.connectionTimeout ||
            e.type == DioExceptionType.sendTimeout ||
            e.type == DioExceptionType.receiveTimeout ||
            e.type == DioExceptionType.connectionError;

        if (!retryable || attempt >= maxRetries) {
          rethrow;
        }

        final delay = _backoffDelay(attempt);
        log('⚠️ $operationName failed (${e.type}) — '
            'retrying in ${delay.inMilliseconds}ms '
            '(attempt ${attempt + 1}/$maxRetries)');
        await Future<void>.delayed(delay);
      }
    }

    // Should not reach here, but satisfy the analyzer
    throw lastError ?? DioException(
      requestOptions: RequestOptions(path: path),
      message: '$operationName exhausted all $maxRetries retries',
    );
  }

  /// Calculate exponential backoff delay: base * 2^attempt, capped at 4s.
  Duration _backoffDelay(int attempt) {
    final ms = _baseDelay.inMilliseconds * (1 << attempt);
    return Duration(milliseconds: min(ms, 4000));
  }
}

