import { randomUUID } from 'crypto';
import { getAppStateStore, setAppState } from '../../state/AppState.js';
import { logForDebugging } from '../../utils/debug.js';
import { TEAM_LEAD_NAME } from '../../utils/swarm/constants.js';
import { getAgentName, isTeamLead, isTeammate } from '../../utils/teammate.js';
import { isInProcessTeammate } from '../../utils/teammateContext.js';
import {
  isPermissionRequest,
  isPermissionResponse,
  isSandboxPermissionRequest,
  isSandboxPermissionResponse,
  isShutdownApproved,
  isTeamPermissionUpdate,
  isModeSetRequest,
  isPlanApprovalRequest,
  markMessagesAsRead,
  readUnreadMessages,
} from '../../utils/teammateMailbox.js';
import { TEAMMATE_MESSAGE_TAG } from '../../constants/xml.js';

const INBOX_POLL_INTERVAL_MS = 1000;

/**
 * Headless controller for teammate inbox polling.
 * Replaces React `useInboxPoller` hook.
 */
export class InboxPollerController {
  private timer: NodeJS.Timeout | null = null;
  private enabled: boolean = false;
  private isLoading: boolean = false;
  private focusedInputDialog: string | undefined = undefined;
  private onSubmitMessage: (formatted: string) => boolean;

  constructor(onSubmitMessage: (formatted: string) => boolean) {
    this.onSubmitMessage = onSubmitMessage;
  }

  setState(enabled: boolean, isLoading: boolean, focusedInputDialog: string | undefined) {
    this.enabled = enabled;
    this.isLoading = isLoading;
    this.focusedInputDialog = focusedInputDialog;
  }

  start() {
    if (this.timer) return;
    this.timer = setInterval(() => void this.poll(), INBOX_POLL_INTERVAL_MS);
    void this.poll(); // Initial poll
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  private getAgentNameToPoll(appState: any): string | undefined {
    if (isInProcessTeammate()) return undefined;
    if (isTeammate()) return getAgentName();
    if (isTeamLead(appState.teamContext)) {
      const leadAgentId = appState.teamContext!.leadAgentId;
      const leadName = appState.teamContext!.teammates[leadAgentId]?.name;
      return leadName || 'team-lead';
    }
    return undefined;
  }

  private async poll() {
    if (!this.enabled) return;

    const store = getAppStateStore();
    const currentAppState = store.getState();
    const agentName = this.getAgentNameToPoll(currentAppState);
    if (!agentName) return;

    const unread = await readUnreadMessages(agentName, currentAppState.teamContext?.teamName);
    if (unread.length === 0) {
      this.flushPendingMessages(currentAppState);
      return;
    }

    logForDebugging(`[InboxPollerController] Found ${unread.length} unread message(s)`);

    const regularMessages: any[] = [];
    for (const m of unread) {
      // Basic sorting logic ported; omitted complex UI interaction flows
      // which would be handled headlessly here based on context
      if (
        isPermissionRequest(m.text) ||
        isPermissionResponse(m.text) ||
        isSandboxPermissionRequest(m.text) ||
        isSandboxPermissionResponse(m.text) ||
        isShutdownApproved(m.text) ||
        isTeamPermissionUpdate(m.text) ||
        isModeSetRequest(m.text) ||
        isPlanApprovalRequest(m.text)
      ) {
        logForDebugging(`[InboxPollerController] Delegating meta request: ${m.from}`);
      } else {
        regularMessages.push(m);
      }
    }

    const markRead = () =>
      void markMessagesAsRead(agentName, currentAppState.teamContext?.teamName);

    if (regularMessages.length === 0) {
      markRead();
      return;
    }

    const formatted = regularMessages
      .map((m: any) => {
        const colorAttr = m.color ? ` color="${m.color}"` : '';
        const summaryAttr = m.summary ? ` summary="${m.summary}"` : '';
        return `<${TEAMMATE_MESSAGE_TAG} teammate_id="${m.from}"${colorAttr}${summaryAttr}>\n${m.text}\n</${TEAMMATE_MESSAGE_TAG}>`;
      })
      .join('\n\n');

    if (!this.isLoading && !this.focusedInputDialog) {
      logForDebugging(`[InboxPollerController] Session idle, submitting immediately`);
      const submitted = this.onSubmitMessage(formatted);
      if (!submitted) {
        this.queueMessages(regularMessages);
      }
    } else {
      this.queueMessages(regularMessages);
    }

    markRead();
  }

  private queueMessages(messages: any[]) {
    setAppState((prev: any) => ({
      ...prev,
      inbox: {
        messages: [
          ...prev.inbox.messages,
          ...messages.map((m) => ({
            id: randomUUID(),
            from: m.from,
            text: m.text,
            timestamp: m.timestamp,
            status: 'pending',
            color: m.color,
            summary: m.summary,
          })),
        ],
      },
    }));
  }

  private flushPendingMessages(currentAppState: any) {
    if (this.isLoading || this.focusedInputDialog) return;

    const pendingMessages = currentAppState.inbox.messages.filter(
      (m: any) => m.status === 'pending',
    );
    if (pendingMessages.length === 0) return;

    const formatted = pendingMessages
      .map((m: any) => {
        const colorAttr = m.color ? ` color="${m.color}"` : '';
        const summaryAttr = m.summary ? ` summary="${m.summary}"` : '';
        return `<${TEAMMATE_MESSAGE_TAG} teammate_id="${m.from}"${colorAttr}${summaryAttr}>\n${m.text}\n</${TEAMMATE_MESSAGE_TAG}>`;
      })
      .join('\n\n');

    const submitted = this.onSubmitMessage(formatted);
    if (submitted) {
      const submittedIds = new Set(pendingMessages.map((m: any) => m.id));
      setAppState((prev: any) => ({
        ...prev,
        inbox: {
          messages: prev.inbox.messages.filter((m: any) => !submittedIds.has(m.id)),
        },
      }));
    }
  }
}
