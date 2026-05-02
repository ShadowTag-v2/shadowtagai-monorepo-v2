import { extractInboundMessageFields } from '../../bridge/inboundMessages.js';
import { setReplBridgeHandle } from '../../bridge/replBridgeHandle.js';
import { getAppStateStore, setAppState } from '../../state/AppState.js';
import { logForDebugging } from '../../utils/debug.js';
import { errorMessage } from '../../utils/errors.js';
import { enqueue } from '../../utils/messageQueueManager.js';

const BRIDGE_FAILURE_DISMISS_MS = 10000;
const MAX_CONSECUTIVE_INIT_FAILURES = 3;

/**
 * Headless controller for REPL bridge (remote control).
 * Replaces React `useReplBridge` hook.
 */
export class ReplBridgeController {
  private handle: any = null;
  private cancelled: boolean = false;
  private consecutiveFailures: number = 0;
  private lastWrittenIndex: number = 0;
  private failureTimeout: NodeJS.Timeout | undefined;

  private messagesProvider: () => any[];

  constructor(messagesProvider: () => any[]) {
    this.messagesProvider = messagesProvider;
  }

  async start() {
    this.cancelled = false;
    const store = getAppStateStore();
    const state = store.getState();

    if (this.consecutiveFailures >= MAX_CONSECUTIVE_INIT_FAILURES) {
      logForDebugging(
        `[ReplBridgeController] Fuse blown after ${this.consecutiveFailures} failures`,
      );
      setAppState((prev: any) => ({ ...prev, replBridgeEnabled: false }));
      return;
    }

    try {
      // Dynamic import simulated for headless
      const { initReplBridge } = await import('../../bridge/initReplBridge.js');

      this.handle = await initReplBridge({
        outboundOnly: state.replBridgeOutboundOnly,
        onInboundMessage: async (msg: any) => {
          try {
            const fields = extractInboundMessageFields(msg);
            if (!fields) return;
            const { resolveAndPrepend } = await import('../../bridge/inboundAttachments.js');
            const content = await resolveAndPrepend(msg, fields.content);
            enqueue({
              value: content,
              mode: 'prompt',
              uuid: fields.uuid,
              skipSlashCommands: true,
              bridgeOrigin: true,
            });
          } catch (e) {
            logForDebugging(`[ReplBridgeController] Inbound msg fail: ${e}`);
          }
        },
        onStateChange: (bridgeState: string, detail?: string) => {
          logForDebugging(`[ReplBridgeController] State: ${bridgeState}`);
          if (bridgeState === 'failed') {
            this.handleFailure();
          }
        },
        initialMessages: this.messagesProvider(),
        getMessages: () => this.messagesProvider(),
      });

      if (this.cancelled) {
        if (this.handle) void this.handle.teardown();
        return;
      }

      if (!this.handle) {
        this.consecutiveFailures++;
        this.handleFailure();
        return;
      }

      setReplBridgeHandle(this.handle);
      this.consecutiveFailures = 0;
      this.lastWrittenIndex = this.messagesProvider().length;
    } catch (err) {
      if (this.cancelled) return;
      this.consecutiveFailures++;
      logForDebugging(`[ReplBridgeController] Init failed: ${errorMessage(err as Error)}`);
      this.handleFailure();
    }
  }

  async stop() {
    this.cancelled = true;
    if (this.failureTimeout) clearTimeout(this.failureTimeout);
    if (this.handle) {
      await this.handle.teardown();
      this.handle = null;
      setReplBridgeHandle(null);
    }
  }

  syncMessages() {
    if (!this.handle) return;
    const messages = this.messagesProvider();
    const startIndex = Math.min(this.lastWrittenIndex, messages.length);
    const newMessages = messages
      .slice(startIndex)
      .filter(
        (m: any) =>
          m.type === 'user' ||
          m.type === 'assistant' ||
          (m.type === 'system' && m.subtype === 'local_command'),
      );

    this.lastWrittenIndex = messages.length;
    if (newMessages.length > 0) {
      this.handle.writeMessages(newMessages);
    }
  }

  private handleFailure() {
    if (this.failureTimeout) clearTimeout(this.failureTimeout);
    this.failureTimeout = setTimeout(() => {
      if (this.cancelled) return;
      setAppState((prev: any) => ({
        ...prev,
        replBridgeEnabled: false,
        replBridgeError: undefined,
      }));
    }, BRIDGE_FAILURE_DISMISS_MS);
  }
}
