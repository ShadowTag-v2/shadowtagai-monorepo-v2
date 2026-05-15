/**
 * Custom hooks index
 * Central export point for all custom hooks
 */

export { useAuth } from './useAuth';
export { useAutoResize } from './useAutoResize';
export type { UseAutoScrollReturn } from './useAutoScroll';
export { useAutoScroll } from './useAutoScroll';
export type { SendMessageParams, UseChatAPIReturn } from './useChatAPI';
export { useChatAPI } from './useChatAPI';
export { useEmbeddedWallet } from './useEmbeddedWallet';
export { useEmbeddedWalletClient } from './useEmbeddedWalletClient';
export type { UseFileUploadReturn } from './useFileUpload';
export { useFileUpload } from './useFileUpload';
export type { UploadedFile, UsePresignedUploadReturn } from './usePresignedUpload';
export { usePresignedUpload } from './usePresignedUpload';
export type { Message, Session, UseSessionsReturn } from './useSessions';
export { useSessions } from './useSessions';
export type {
  ConversationState,
  State,
  StateValues,
  ToolState,
  UseStatesReturn,
} from './useStates';
export { useStates } from './useStates';
export { useToast } from './useToast';
export type { UseTypingAnimationReturn } from './useTypingAnimation';
export { useTypingAnimation } from './useTypingAnimation';
export type { UseWebSocketReturn, WebSocketMessage } from './useWebSocket';
export { useWebSocket } from './useWebSocket';
export type { UseX402PaymentReturn } from './useX402Payment';
export { useX402Payment } from './useX402Payment';
