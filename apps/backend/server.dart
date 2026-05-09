import 'dart:convert';
import 'dart:io';

/// V25 Pinnacle — Sovereign Dart Backend
/// Processes autonomic CDC events from Pub/Sub push subscriptions.
/// Runs natively on Cloud Run as a Dart shelf server.

Future<void> main() async {
  final port = int.parse(Platform.environment['PORT'] ?? '8080');
  final server = await HttpServer.bind('0.0.0.0', port);

  print('shadowtag-omega-v4 Dart OS Compute Active on port $port');

  await for (final request in server) {
    try {
      if (request.uri.path == '/pubsub/push' && request.method == 'POST') {
        final body = await utf8.decoder.bind(request).join();
        final payload = jsonDecode(body) as Map<String, dynamic>;

        final messageData = payload['message']?['data'] as String? ?? '';
        final decoded = utf8.decode(base64Decode(messageData));

        final attributes = payload['message']?['attributes'] as Map<String, dynamic>?;
        final eventType = attributes?['eventType'] ?? 'UNKNOWN';

        print('[AUDIT] CDC Event ($eventType): $decoded');

        request.response
          ..statusCode = HttpStatus.ok
          ..headers.contentType = ContentType.text
          ..write('Event Processed natively in Dart OS.')
          ..close();
      } else if (request.uri.path == '/health') {
        request.response
          ..statusCode = HttpStatus.ok
          ..headers.contentType = ContentType.json
          ..write(jsonEncode({
            'status': 'healthy',
            'runtime': 'dart',
            'version': 'V25-Pinnacle',
            'timestamp': DateTime.now().toUtc().toIso8601String(),
          }))
          ..close();
      } else {
        request.response
          ..statusCode = HttpStatus.notFound
          ..write('Endpoint not found.')
          ..close();
      }
    } catch (e) {
      print('[ERROR] Request handler failed: $e');
      request.response
        ..statusCode = HttpStatus.internalServerError
        ..write('Internal Server Error')
        ..close();
    }
  }
}
