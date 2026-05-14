// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from "../../../core/resource";
import * as SessionsAPI from "./sessions";
import { SessionCreateParams, Sessions } from "./sessions";
import * as ThreadsAPI from "./threads";
import {
  ChatKitAttachment,
  ChatKitResponseOutputText,
  ChatKitThread,
  ChatKitThreadAssistantMessageItem,
  ChatKitThreadItemList,
  ChatKitThreadItemListDataPage,
  ChatKitThreadsPage,
  ChatKitThreadUserMessageItem,
  ChatKitWidgetItem,
  ChatSession,
  ChatSessionAutomaticThreadTitling,
  ChatSessionChatKitConfiguration,
  ChatSessionChatKitConfigurationParam,
  ChatSessionExpiresAfterParam,
  ChatSessionFileUpload,
  ChatSessionHistory,
  ChatSessionRateLimits,
  ChatSessionRateLimitsParam,
  ChatSessionStatus,
  ChatSessionWorkflowParam,
  ThreadDeleteResponse,
  ThreadListItemsParams,
  ThreadListParams,
  Threads,
} from "./threads";

export class ChatKit extends APIResource {
  sessions: SessionsAPI.Sessions = new SessionsAPI.Sessions(this._client);
  threads: ThreadsAPI.Threads = new ThreadsAPI.Threads(this._client);
}

/**
 * Workflow metadata and state returned for the session.
 */
export interface ChatKitWorkflow {
  /**
   * Identifier of the workflow backing the session.
   */
  id: string;

  /**
   * State variable key-value pairs applied when invoking the workflow. Defaults to
   * null when no overrides were provided.
   */
  state_variables: { [key: string]: string | boolean | number } | null;

  /**
   * Tracing settings applied to the workflow.
   */
  tracing: ChatKitWorkflow.Tracing;

  /**
   * Specific workflow version used for the session. Defaults to null when using the
   * latest deployment.
   */
  version: string | null;
}

export namespace ChatKitWorkflow {
  /**
   * Tracing settings applied to the workflow.
   */
  export interface Tracing {
    /**
     * Indicates whether tracing is enabled.
     */
    enabled: boolean;
  }
}

ChatKit.Sessions = Sessions;
ChatKit.Threads = Threads;

export declare namespace ChatKit {
  export {
    ChatKitAttachment,
    ChatKitResponseOutputText,
    ChatKitThread,
    ChatKitThreadAssistantMessageItem,
    ChatKitThreadItemList,
    ChatKitThreadItemListDataPage,
    ChatKitThreadsPage,
    ChatKitThreadUserMessageItem,
    ChatKitWidgetItem,
    ChatKitWorkflow,
    ChatSession,
    ChatSessionAutomaticThreadTitling,
    ChatSessionChatKitConfiguration,
    ChatSessionChatKitConfigurationParam,
    ChatSessionExpiresAfterParam,
    ChatSessionFileUpload,
    ChatSessionHistory,
    ChatSessionRateLimits,
    ChatSessionRateLimitsParam,
    ChatSessionStatus,
    ChatSessionWorkflowParam,
    SessionCreateParams,
    Sessions,
    ThreadDeleteResponse,
    ThreadListItemsParams,
    ThreadListParams,
    Threads,
  };
}
