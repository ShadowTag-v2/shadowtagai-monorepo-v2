import { getAppStateStore, setAppState } from "../../state/AppState.js";
import { isTerminalTaskStatus } from "../../Task.js";
import {
  findTeammateTaskByAgentId,
  injectUserMessageToTeammate,
} from "../../tasks/InProcessTeammateTask/InProcessTeammateTask.js";
import { isKairosCronEnabled } from "../../tools/ScheduleCronTool/prompt.js";
import type { Message } from "../../types/message.js";
import { getCronJitterConfig } from "../../utils/cronJitterConfig.js";
import { createCronScheduler } from "../../utils/cronScheduler.js";
import { removeCronTasks } from "../../utils/cronTasks.js";
import { logForDebugging } from "../../utils/debug.js";
import { enqueuePendingNotification } from "../../utils/messageQueueManager.js";
import { createScheduledTaskFireMessage } from "../../utils/messages.js";
import { WORKLOAD_CRON } from "../../utils/workloadContext.js";

/**
 * Headless controller for scheduled cron tasks.
 * Replaces React `useScheduledTasks` hook.
 */
export class ScheduledTasksController {
  private scheduler: any = null;
  private isLoadingState: boolean = false;
  private assistantMode: boolean;
  private onMessage: (message: Message) => void;

  constructor(assistantMode: boolean = false, onMessage: (message: Message) => void) {
    this.assistantMode = assistantMode;
    this.onMessage = onMessage;
  }

  setIsLoading(isLoading: boolean) {
    this.isLoadingState = isLoading;
  }

  start() {
    if (!isKairosCronEnabled()) return;

    const enqueueForLead = (prompt: string) =>
      enqueuePendingNotification({
        value: prompt,
        mode: "prompt",
        priority: "later",
        isMeta: true,
        workload: WORKLOAD_CRON,
      });

    this.scheduler = createCronScheduler({
      onFire: enqueueForLead,
      onFireTask: (task: any) => {
        const store = getAppStateStore();
        if (task.agentId) {
          const teammate = findTeammateTaskByAgentId(task.agentId, store.getState().tasks);
          if (teammate && !isTerminalTaskStatus(teammate.status)) {
            injectUserMessageToTeammate(teammate.id, task.prompt, setAppState);
            return;
          }
          logForDebugging(
            `[ScheduledTasksController] teammate ${task.agentId} gone, removing orphaned cron ${task.id}`,
          );
          void removeCronTasks([task.id]);
          return;
        }

        const msg = createScheduledTaskFireMessage(
          `Running scheduled task (${this.formatCronFireTime(new Date())})`,
        );
        this.onMessage(msg);
        enqueueForLead(task.prompt);
      },
      isLoading: () => this.isLoadingState,
      assistantMode: this.assistantMode,
      getJitterConfig: getCronJitterConfig,
      isKilled: () => !isKairosCronEnabled(),
    });

    this.scheduler.start();
  }

  stop() {
    if (this.scheduler) {
      this.scheduler.stop();
      this.scheduler = null;
    }
  }

  private formatCronFireTime(d: Date): string {
    return d
      .toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      })
      .replace(/,? at |, /, " ")
      .replace(/ ([AP]M)/, (_, ampm) => ampm.toLowerCase());
  }
}
