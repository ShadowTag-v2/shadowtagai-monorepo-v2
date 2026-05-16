// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from "../../core/resource";
import * as FilesAPI from "./files";
import {
  DeletedFile,
  FileDeleteParams,
  FileDownloadParams,
  FileListParams,
  FileMetadata,
  FileMetadataPage,
  FileRetrieveMetadataParams,
  Files,
  FileUploadParams,
} from "./files";
import * as MessagesAPI from "./messages/messages";
import {
  BetaAllThinkingTurns,
  BetaBase64ImageSource,
  BetaBase64PDFBlock,
  BetaBase64PDFSource,
  BetaBashCodeExecutionOutputBlock,
  BetaBashCodeExecutionOutputBlockParam,
  BetaBashCodeExecutionResultBlock,
  BetaBashCodeExecutionResultBlockParam,
  BetaBashCodeExecutionToolResultBlock,
  BetaBashCodeExecutionToolResultBlockParam,
  BetaBashCodeExecutionToolResultError,
  BetaBashCodeExecutionToolResultErrorParam,
  BetaCacheControlEphemeral,
  BetaCacheCreation,
  BetaCitationCharLocation,
  BetaCitationCharLocationParam,
  BetaCitationConfig,
  BetaCitationContentBlockLocation,
  BetaCitationContentBlockLocationParam,
  BetaCitationPageLocation,
  BetaCitationPageLocationParam,
  BetaCitationSearchResultLocation,
  BetaCitationSearchResultLocationParam,
  BetaCitationsConfigParam,
  BetaCitationsDelta,
  BetaCitationsWebSearchResultLocation,
  BetaCitationWebSearchResultLocationParam,
  BetaClearThinking20251015Edit,
  BetaClearThinking20251015EditResponse,
  BetaClearToolUses20250919Edit,
  BetaClearToolUses20250919EditResponse,
  BetaCodeExecutionOutputBlock,
  BetaCodeExecutionOutputBlockParam,
  BetaCodeExecutionResultBlock,
  BetaCodeExecutionResultBlockParam,
  BetaCodeExecutionTool20250522,
  BetaCodeExecutionTool20250825,
  BetaCodeExecutionToolResultBlock,
  BetaCodeExecutionToolResultBlockContent,
  BetaCodeExecutionToolResultBlockParam,
  BetaCodeExecutionToolResultBlockParamContent,
  BetaCodeExecutionToolResultError,
  BetaCodeExecutionToolResultErrorCode,
  BetaCodeExecutionToolResultErrorParam,
  BetaContainer,
  BetaContainerParams,
  BetaContainerUploadBlock,
  BetaContainerUploadBlockParam,
  BetaContentBlock,
  BetaContentBlockParam,
  BetaContentBlockSource,
  BetaContentBlockSourceContent,
  BetaContextManagementConfig,
  BetaContextManagementResponse,
  BetaCountTokensContextManagementResponse,
  BetaDirectCaller,
  BetaDocumentBlock,
  BetaFileDocumentSource,
  BetaFileImageSource,
  BetaImageBlockParam,
  BetaInputJSONDelta,
  BetaInputTokensClearAtLeast,
  BetaInputTokensTrigger,
  BetaJSONOutputFormat,
  BetaMCPToolConfig,
  BetaMCPToolDefaultConfig,
  BetaMCPToolResultBlock,
  BetaMCPToolset,
  BetaMCPToolUseBlock,
  BetaMCPToolUseBlockParam,
  BetaMemoryTool20250818,
  BetaMemoryTool20250818Command,
  BetaMemoryTool20250818CreateCommand,
  BetaMemoryTool20250818DeleteCommand,
  BetaMemoryTool20250818InsertCommand,
  BetaMemoryTool20250818RenameCommand,
  BetaMemoryTool20250818StrReplaceCommand,
  BetaMemoryTool20250818ViewCommand,
  BetaMessage,
  BetaMessageDeltaUsage,
  BetaMessageParam,
  BetaMessageTokensCount,
  BetaMetadata,
  BetaOutputConfig,
  BetaPlainTextSource,
  BetaRawContentBlockDelta,
  BetaRawContentBlockDeltaEvent,
  BetaRawContentBlockStartEvent,
  BetaRawContentBlockStopEvent,
  BetaRawMessageDeltaEvent,
  BetaRawMessageStartEvent,
  BetaRawMessageStopEvent,
  BetaRawMessageStreamEvent,
  BetaRedactedThinkingBlock,
  BetaRedactedThinkingBlockParam,
  BetaRequestDocumentBlock,
  BetaRequestMCPServerToolConfiguration,
  BetaRequestMCPServerURLDefinition,
  BetaRequestMCPToolResultBlockParam,
  BetaSearchResultBlockParam,
  BetaServerToolCaller,
  BetaServerToolUsage,
  BetaServerToolUseBlock,
  BetaServerToolUseBlockParam,
  BetaSignatureDelta,
  BetaSkill,
  BetaSkillParams,
  BetaStopReason,
  BetaTextBlock,
  BetaTextBlockParam,
  BetaTextCitation,
  BetaTextCitationParam,
  BetaTextDelta,
  BetaTextEditorCodeExecutionCreateResultBlock,
  BetaTextEditorCodeExecutionCreateResultBlockParam,
  BetaTextEditorCodeExecutionStrReplaceResultBlock,
  BetaTextEditorCodeExecutionStrReplaceResultBlockParam,
  BetaTextEditorCodeExecutionToolResultBlock,
  BetaTextEditorCodeExecutionToolResultBlockParam,
  BetaTextEditorCodeExecutionToolResultError,
  BetaTextEditorCodeExecutionToolResultErrorParam,
  BetaTextEditorCodeExecutionViewResultBlock,
  BetaTextEditorCodeExecutionViewResultBlockParam,
  BetaThinkingBlock,
  BetaThinkingBlockParam,
  BetaThinkingConfigDisabled,
  BetaThinkingConfigEnabled,
  BetaThinkingConfigParam,
  BetaThinkingDelta,
  BetaThinkingTurns,
  BetaTool,
  BetaToolBash20241022,
  BetaToolBash20250124,
  BetaToolChoice,
  BetaToolChoiceAny,
  BetaToolChoiceAuto,
  BetaToolChoiceNone,
  BetaToolChoiceTool,
  BetaToolComputerUse20241022,
  BetaToolComputerUse20250124,
  BetaToolComputerUse20251124,
  BetaToolReferenceBlock,
  BetaToolReferenceBlockParam,
  BetaToolResultBlockParam,
  BetaToolTextEditor20241022,
  BetaToolTextEditor20250124,
  BetaToolTextEditor20250429,
  BetaToolTextEditor20250728,
  BetaToolUnion,
  BetaToolUseBlock,
  BetaToolUseBlockParam,
  BetaToolUsesKeep,
  BetaToolUsesTrigger,
  BetaURLImageSource,
  BetaURLPDFSource,
  BetaUsage,
  BetaWebFetchBlock,
  BetaWebFetchBlockParam,
  BetaWebFetchTool20250910,
  BetaWebFetchToolResultBlock,
  BetaWebFetchToolResultBlockParam,
  BetaWebFetchToolResultErrorBlock,
  BetaWebFetchToolResultErrorBlockParam,
  BetaWebFetchToolResultErrorCode,
  BetaWebSearchResultBlock,
  BetaWebSearchResultBlockParam,
  BetaWebSearchTool20250305,
  BetaWebSearchToolRequestError,
  BetaWebSearchToolResultBlock,
  BetaWebSearchToolResultBlockContent,
  BetaWebSearchToolResultBlockParam,
  BetaWebSearchToolResultBlockParamContent,
  BetaWebSearchToolResultError,
  BetaWebSearchToolResultErrorCode,
  MessageCountTokensParams,
  MessageCreateParams,
  MessageCreateParamsNonStreaming,
  MessageCreateParamsStreaming,
  Messages,
} from "./messages/messages";
import * as ModelsAPI from "./models";
import {
  BetaModelInfo,
  BetaModelInfosPage,
  ModelListParams,
  ModelRetrieveParams,
  Models,
} from "./models";
import * as SkillsAPI from "./skills/skills";
import {
  SkillCreateParams,
  SkillCreateResponse,
  SkillDeleteParams,
  SkillDeleteResponse,
  SkillListParams,
  SkillListResponse,
  SkillListResponsesPageCursor,
  SkillRetrieveParams,
  SkillRetrieveResponse,
  Skills,
} from "./skills/skills";

export class Beta extends APIResource {
  models: ModelsAPI.Models = new ModelsAPI.Models(this._client);
  messages: MessagesAPI.Messages = new MessagesAPI.Messages(this._client);
  files: FilesAPI.Files = new FilesAPI.Files(this._client);
  skills: SkillsAPI.Skills = new SkillsAPI.Skills(this._client);
}

export type AnthropicBeta =
  | (string & {})
  | "message-batches-2024-09-24"
  | "prompt-caching-2024-07-31"
  | "computer-use-2024-10-22"
  | "computer-use-2025-01-24"
  | "pdfs-2024-09-25"
  | "token-counting-2024-11-01"
  | "token-efficient-tools-2025-02-19"
  | "output-128k-2025-02-19"
  | "files-api-2025-04-14"
  | "mcp-client-2025-04-04"
  | "mcp-client-2025-11-20"
  | "dev-full-thinking-2025-05-14"
  | "interleaved-thinking-2025-05-14"
  | "code-execution-2025-05-22"
  | "extended-cache-ttl-2025-04-11"
  | "context-1m-2025-08-07"
  | "context-management-2025-06-27"
  | "model-context-window-exceeded-2025-08-26"
  | "skills-2025-10-02";

export interface BetaAPIError {
  message: string;

  type: "api_error";
}

export interface BetaAuthenticationError {
  message: string;

  type: "authentication_error";
}

export interface BetaBillingError {
  message: string;

  type: "billing_error";
}

export type BetaError =
  | BetaInvalidRequestError
  | BetaAuthenticationError
  | BetaBillingError
  | BetaPermissionError
  | BetaNotFoundError
  | BetaRateLimitError
  | BetaGatewayTimeoutError
  | BetaAPIError
  | BetaOverloadedError;

export interface BetaErrorResponse {
  error: BetaError;

  request_id: string | null;

  type: "error";
}

export interface BetaGatewayTimeoutError {
  message: string;

  type: "timeout_error";
}

export interface BetaInvalidRequestError {
  message: string;

  type: "invalid_request_error";
}

export interface BetaNotFoundError {
  message: string;

  type: "not_found_error";
}

export interface BetaOverloadedError {
  message: string;

  type: "overloaded_error";
}

export interface BetaPermissionError {
  message: string;

  type: "permission_error";
}

export interface BetaRateLimitError {
  message: string;

  type: "rate_limit_error";
}

Beta.Models = Models;
Beta.Messages = Messages;
Beta.Files = Files;
Beta.Skills = Skills;

export declare namespace Beta {
  export {
    type AnthropicBeta,
    BetaAllThinkingTurns,
    type BetaAPIError,
    type BetaAuthenticationError,
    BetaBase64ImageSource,
    BetaBase64PDFBlock,
    BetaBase64PDFSource,
    BetaBashCodeExecutionOutputBlock,
    BetaBashCodeExecutionOutputBlockParam,
    BetaBashCodeExecutionResultBlock,
    BetaBashCodeExecutionResultBlockParam,
    BetaBashCodeExecutionToolResultBlock,
    BetaBashCodeExecutionToolResultBlockParam,
    BetaBashCodeExecutionToolResultError,
    BetaBashCodeExecutionToolResultErrorParam,
    type BetaBillingError,
    BetaCacheControlEphemeral,
    BetaCacheCreation,
    BetaCitationCharLocation,
    BetaCitationCharLocationParam,
    BetaCitationConfig,
    BetaCitationContentBlockLocation,
    BetaCitationContentBlockLocationParam,
    BetaCitationPageLocation,
    BetaCitationPageLocationParam,
    BetaCitationSearchResultLocation,
    BetaCitationSearchResultLocationParam,
    BetaCitationsConfigParam,
    BetaCitationsDelta,
    BetaCitationsWebSearchResultLocation,
    BetaCitationWebSearchResultLocationParam,
    BetaClearThinking20251015Edit,
    BetaClearThinking20251015EditResponse,
    BetaClearToolUses20250919Edit,
    BetaClearToolUses20250919EditResponse,
    BetaCodeExecutionOutputBlock,
    BetaCodeExecutionOutputBlockParam,
    BetaCodeExecutionResultBlock,
    BetaCodeExecutionResultBlockParam,
    BetaCodeExecutionTool20250522,
    BetaCodeExecutionTool20250825,
    BetaCodeExecutionToolResultBlock,
    BetaCodeExecutionToolResultBlockContent,
    BetaCodeExecutionToolResultBlockParam,
    BetaCodeExecutionToolResultBlockParamContent,
    BetaCodeExecutionToolResultError,
    BetaCodeExecutionToolResultErrorCode,
    BetaCodeExecutionToolResultErrorParam,
    BetaContainer,
    BetaContainerParams,
    BetaContainerUploadBlock,
    BetaContainerUploadBlockParam,
    BetaContentBlock,
    BetaContentBlockParam,
    BetaContentBlockSource,
    BetaContentBlockSourceContent,
    BetaContextManagementConfig,
    BetaContextManagementResponse,
    BetaCountTokensContextManagementResponse,
    BetaDirectCaller,
    BetaDocumentBlock,
    type BetaError,
    type BetaErrorResponse,
    BetaFileDocumentSource,
    BetaFileImageSource,
    type BetaGatewayTimeoutError,
    BetaImageBlockParam,
    BetaInputJSONDelta,
    BetaInputTokensClearAtLeast,
    BetaInputTokensTrigger,
    type BetaInvalidRequestError,
    BetaJSONOutputFormat,
    BetaMCPToolConfig,
    BetaMCPToolDefaultConfig,
    BetaMCPToolResultBlock,
    BetaMCPToolset,
    BetaMCPToolUseBlock,
    BetaMCPToolUseBlockParam,
    BetaMemoryTool20250818,
    BetaMemoryTool20250818Command,
    BetaMemoryTool20250818CreateCommand,
    BetaMemoryTool20250818DeleteCommand,
    BetaMemoryTool20250818InsertCommand,
    BetaMemoryTool20250818RenameCommand,
    BetaMemoryTool20250818StrReplaceCommand,
    BetaMemoryTool20250818ViewCommand,
    BetaMessage,
    BetaMessageDeltaUsage,
    BetaMessageParam,
    BetaMessageTokensCount,
    BetaMetadata,
    BetaModelInfo,
    BetaModelInfosPage,
    type BetaNotFoundError,
    BetaOutputConfig,
    type BetaOverloadedError,
    type BetaPermissionError,
    BetaPlainTextSource,
    type BetaRateLimitError,
    BetaRawContentBlockDelta,
    BetaRawContentBlockDeltaEvent,
    BetaRawContentBlockStartEvent,
    BetaRawContentBlockStopEvent,
    BetaRawMessageDeltaEvent,
    BetaRawMessageStartEvent,
    BetaRawMessageStopEvent,
    BetaRawMessageStreamEvent,
    BetaRedactedThinkingBlock,
    BetaRedactedThinkingBlockParam,
    BetaRequestDocumentBlock,
    BetaRequestMCPServerToolConfiguration,
    BetaRequestMCPServerURLDefinition,
    BetaRequestMCPToolResultBlockParam,
    BetaSearchResultBlockParam,
    BetaServerToolCaller,
    BetaServerToolUsage,
    BetaServerToolUseBlock,
    BetaServerToolUseBlockParam,
    BetaSignatureDelta,
    BetaSkill,
    BetaSkillParams,
    BetaStopReason,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaTextCitation,
    BetaTextCitationParam,
    BetaTextDelta,
    BetaTextEditorCodeExecutionCreateResultBlock,
    BetaTextEditorCodeExecutionCreateResultBlockParam,
    BetaTextEditorCodeExecutionStrReplaceResultBlock,
    BetaTextEditorCodeExecutionStrReplaceResultBlockParam,
    BetaTextEditorCodeExecutionToolResultBlock,
    BetaTextEditorCodeExecutionToolResultBlockParam,
    BetaTextEditorCodeExecutionToolResultError,
    BetaTextEditorCodeExecutionToolResultErrorParam,
    BetaTextEditorCodeExecutionViewResultBlock,
    BetaTextEditorCodeExecutionViewResultBlockParam,
    BetaThinkingBlock,
    BetaThinkingBlockParam,
    BetaThinkingConfigDisabled,
    BetaThinkingConfigEnabled,
    BetaThinkingConfigParam,
    BetaThinkingDelta,
    BetaThinkingTurns,
    BetaTool,
    BetaToolBash20241022,
    BetaToolBash20250124,
    BetaToolChoice,
    BetaToolChoiceAny,
    BetaToolChoiceAuto,
    BetaToolChoiceNone,
    BetaToolChoiceTool,
    BetaToolComputerUse20241022,
    BetaToolComputerUse20250124,
    BetaToolComputerUse20251124,
    BetaToolReferenceBlock,
    BetaToolReferenceBlockParam,
    BetaToolResultBlockParam,
    BetaToolTextEditor20241022,
    BetaToolTextEditor20250124,
    BetaToolTextEditor20250429,
    BetaToolTextEditor20250728,
    BetaToolUnion,
    BetaToolUseBlock,
    BetaToolUseBlockParam,
    BetaToolUsesKeep,
    BetaToolUsesTrigger,
    BetaURLImageSource,
    BetaURLPDFSource,
    BetaUsage,
    BetaWebFetchBlock,
    BetaWebFetchBlockParam,
    BetaWebFetchTool20250910,
    BetaWebFetchToolResultBlock,
    BetaWebFetchToolResultBlockParam,
    BetaWebFetchToolResultErrorBlock,
    BetaWebFetchToolResultErrorBlockParam,
    BetaWebFetchToolResultErrorCode,
    BetaWebSearchResultBlock,
    BetaWebSearchResultBlockParam,
    BetaWebSearchTool20250305,
    BetaWebSearchToolRequestError,
    BetaWebSearchToolResultBlock,
    BetaWebSearchToolResultBlockContent,
    BetaWebSearchToolResultBlockParam,
    BetaWebSearchToolResultBlockParamContent,
    BetaWebSearchToolResultError,
    BetaWebSearchToolResultErrorCode,
    DeletedFile,
    FileDeleteParams,
    FileDownloadParams,
    FileListParams,
    FileMetadata,
    FileMetadataPage,
    FileRetrieveMetadataParams,
    Files,
    FileUploadParams,
    MessageCountTokensParams,
    MessageCreateParams,
    MessageCreateParamsNonStreaming,
    MessageCreateParamsStreaming,
    Messages,
    ModelListParams,
    ModelRetrieveParams,
    Models,
    SkillCreateParams,
    SkillCreateResponse,
    SkillDeleteParams,
    SkillDeleteResponse,
    SkillListParams,
    SkillListResponse,
    SkillListResponsesPageCursor,
    SkillRetrieveParams,
    SkillRetrieveResponse,
    Skills,
  };
}
