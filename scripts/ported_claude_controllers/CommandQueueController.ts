import type { QueuedCommand } from "../../types/textInputTypes.js";
import {
  getCommandQueueSnapshot,
  subscribeToCommandQueue,
} from "../../utils/messageQueueManager.js";

/**
 * Headless controller to subscribe to the unified command queue.
 * Replaces React `useCommandQueue` hook.
 */
export class CommandQueueController {
  private unsubscribe: (() => void) | null = null;
  private onQueueChange: (commands: readonly QueuedCommand[]) => void;

  constructor(onQueueChange: (commands: readonly QueuedCommand[]) => void) {
    this.onQueueChange = onQueueChange;
  }

  start() {
    if (this.unsubscribe) return;
    this.unsubscribe = subscribeToCommandQueue(() => {
      const snapshot = getCommandQueueSnapshot();
      this.onQueueChange(snapshot);
    });
    // Trigger initial snapshot
    this.onQueueChange(getCommandQueueSnapshot());
  }

  stop() {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = null;
    }
  }

  getSnapshot(): readonly QueuedCommand[] {
    return getCommandQueueSnapshot();
  }
}
