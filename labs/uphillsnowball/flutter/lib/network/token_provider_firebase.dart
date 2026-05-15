// flutter/lib/network/token_provider_firebase.dart
//
// Firebase Auth Token Provider — Wires OmegaDioClient to Firebase Auth
//
// This bridges the gap between OmegaDioClient's TokenProvider typedef
// and Firebase Auth's getIdToken(forceRefresh) API. The client never
// imports firebase_auth directly — this module is the only coupling point.

import 'package:firebase_auth/firebase_auth.dart';

import 'omega_dio_client.dart';

/// Creates a [TokenProvider] backed by Firebase Auth.
///
/// When invoked (e.g., on a 401 response), this provider:
/// 1. Gets the current Firebase Auth user
/// 2. Calls `getIdToken(true)` to force a token refresh
/// 3. Returns the fresh ID token string
///
/// Returns `null` if no user is signed in, allowing the interceptor
/// to gracefully skip the retry and propagate the 401.
///
/// Usage:
/// ```dart
/// final client = OmegaDioClient(
///   baseUrl: 'https://api.example.com',
///   tenantId: tenantId,
///   tokenProvider: firebaseTokenProvider(),
/// );
/// ```
TokenProvider firebaseTokenProvider({
  FirebaseAuth? authInstance,
}) {
  final auth = authInstance ?? FirebaseAuth.instance;

  return () async {
    final user = auth.currentUser;
    if (user == null) {
      return null;
    }
    // forceRefresh: true ensures we get a fresh token from Firebase,
    // not the locally cached one that just got rejected by 401.
    return user.getIdToken(true);
  };
}

/// Creates an [OmegaDioClient] pre-wired with Firebase Auth token refresh.
///
/// This is the recommended factory for production Flutter apps:
/// ```dart
/// final client = createOmegaClient(
///   baseUrl: 'https://counselconduit-api.run.app',
///   tenantId: 'tenant-abc',
/// );
/// ```
OmegaDioClient createOmegaClient({
  required String baseUrl,
  required String tenantId,
  String modelLock = 'gemini-3.1-flash-lite-preview-thinking',
  FirebaseAuth? authInstance,
}) {
  return OmegaDioClient(
    baseUrl: baseUrl,
    tenantId: tenantId,
    modelLock: modelLock,
    tokenProvider: firebaseTokenProvider(authInstance: authInstance),
  );
}
