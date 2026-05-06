// Copyright 2026 ShadowTagAI
//
// Genkit Dart MCP Server for UphillSnowball
//
// Exposes ShadowTagAI's Genkit actions (tools, prompts, resources) as an MCP
// server over stdio, enabling IDE-native AI development capabilities.
//
// See: https://genkit.dev/docs/dart/mcp

import 'dart:async';
import 'dart:io';

import 'package:genkit/genkit.dart';
import 'package:genkit_mcp/genkit_mcp.dart';

Future<void> main() async {
  final ai = Genkit();

  // Register sovereign AI tools for the UphillSnowball platform.
  ai.defineTool(
    name: 'uphillsnowball_status',
    description:
        'Returns the operational status of the UphillSnowball platform.',
    inputSchema: .map(.string(), .dynamicSchema()),
    fn: (input, _) async {
      return 'platform=UphillSnowball, status=operational, '
          'runtime=Apple Silicon, project=shadowtag-omega-v4, '
          'model=gemini-3.1-flash-lite-preview';
    },
  );

  ai.defineResource(
    name: 'platform_info',
    uri: 'uphillsnowball://info',
    fn: (_, _) async {
      return ResourceOutput(
        content: [
          TextPart(
            text: 'UphillSnowball Platform — Sovereign AI Infrastructure '
                'by ShadowTagAI. Incorporated January 29, 2026.',
          ),
        ],
      );
    },
  );

  // Create and start the MCP server (stdio transport by default).
  final server = createMcpServer(
    ai,
    McpServerOptions(name: 'uphillsnowball-genkit', version: '0.1.0'),
  );
  await server.start();

  // Graceful shutdown on signals.
  final completer = Completer<void>();
  void handleSignal(ProcessSignal _) {
    if (!completer.isCompleted) {
      completer.complete();
    }
  }

  ProcessSignal.sigterm.watch().listen(handleSignal);
  ProcessSignal.sigint.watch().listen(handleSignal);

  await completer.future;
  await server.close();
}
