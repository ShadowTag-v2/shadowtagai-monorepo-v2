/**
 * EvaporatingChatBubble — Privilege-Preserving Chat Component
 * 
 * Implements auto-destructing chat messages with configurable TTL
 * to comply with Heppner (S.D.N.Y. 2026) attorney-client privilege
 * preservation requirements.
 * 
 * Features:
 * - 60-minute default TTL with visual countdown
 * - Privilege level indicators (Work Product / A-C / Confidential)
 * - Progressive opacity fade as TTL approaches
 * - "Preserve" action to extend or persist critical messages
 * - Firestore-backed TTL enforcement (server-side deletion)
 * 
 * @module EvaporatingChatBubble
 * @version 1.0.0
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';

// ============================================================================
// Types
// ============================================================================

export type PrivilegeLevel =
  | 'attorney_work_product'
  | 'attorney_client'
  | 'confidential'
  | 'public';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  privilegeLevel: PrivilegeLevel;
  createdAt: number; // Unix timestamp (ms)
  ttlMs: number;     // Time-to-live in milliseconds
  preserved?: boolean;
  firmId: string;
  sandboxId: string;
}

interface EvaporatingChatBubbleProps {
  message: ChatMessage;
  onExpire: (messageId: string) => void;
  onPreserve?: (messageId: string) => void;
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const DEFAULT_TTL_MS = 60 * 60 * 1000; // 60 minutes
const FADE_START_PERCENT = 0.25; // Start fading at 25% TTL remaining
const WARNING_THRESHOLD_MS = 5 * 60 * 1000; // 5 minutes
const CRITICAL_THRESHOLD_MS = 60 * 1000; // 1 minute

const PRIVILEGE_CONFIG: Record<PrivilegeLevel, {
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
}> = {
  attorney_work_product: {
    label: 'WORK PRODUCT',
    color: '#DC2626',
    bgColor: 'rgba(220, 38, 38, 0.08)',
    borderColor: 'rgba(220, 38, 38, 0.3)',
    icon: '🔒',
  },
  attorney_client: {
    label: 'A-C PRIVILEGE',
    color: '#D97706',
    bgColor: 'rgba(217, 119, 6, 0.08)',
    borderColor: 'rgba(217, 119, 6, 0.3)',
    icon: '🛡️',
  },
  confidential: {
    label: 'CONFIDENTIAL',
    color: '#2563EB',
    bgColor: 'rgba(37, 99, 235, 0.08)',
    borderColor: 'rgba(37, 99, 235, 0.3)',
    icon: '📋',
  },
  public: {
    label: 'PUBLIC',
    color: '#6B7280',
    bgColor: 'rgba(107, 114, 128, 0.08)',
    borderColor: 'rgba(107, 114, 128, 0.3)',
    icon: '📄',
  },
};

// ============================================================================
// Component
// ============================================================================

export const EvaporatingChatBubble: React.FC<EvaporatingChatBubbleProps> = ({
  message,
  onExpire,
  onPreserve,
  className = '',
}) => {
  const [remainingMs, setRemainingMs] = useState<number>(
    message.ttlMs - (Date.now() - message.createdAt)
  );
  const [isHovered, setIsHovered] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // TTL countdown
  useEffect(() => {
    if (message.preserved) return;

    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - message.createdAt;
      const remaining = message.ttlMs - elapsed;

      if (remaining <= 0) {
        if (timerRef.current) clearInterval(timerRef.current);
        onExpire(message.id);
        return;
      }

      setRemainingMs(remaining);
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [message, onExpire]);

  // Calculate opacity based on remaining TTL
  const getOpacity = useCallback((): number => {
    if (message.preserved) return 1;
    const ratio = remainingMs / message.ttlMs;
    if (ratio > FADE_START_PERCENT) return 1;
    return Math.max(0.15, ratio / FADE_START_PERCENT);
  }, [remainingMs, message.ttlMs, message.preserved]);

  // Format remaining time
  const formatRemaining = useCallback((): string => {
    if (message.preserved) return '∞ Preserved';
    if (remainingMs <= 0) return 'Evaporating...';

    const totalSeconds = Math.floor(remainingMs / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    if (minutes > 0) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  }, [remainingMs, message.preserved]);

  // Determine urgency state
  const getUrgencyClass = useCallback((): string => {
    if (message.preserved) return 'preserved';
    if (remainingMs <= CRITICAL_THRESHOLD_MS) return 'critical';
    if (remainingMs <= WARNING_THRESHOLD_MS) return 'warning';
    return 'normal';
  }, [remainingMs, message.preserved]);

  const config = PRIVILEGE_CONFIG[message.privilegeLevel];
  const opacity = getOpacity();
  const urgency = getUrgencyClass();
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={`evaporating-bubble ${isAssistant ? 'assistant' : 'user'} ${urgency} ${className}`}
      style={{
        opacity,
        backgroundColor: config.bgColor,
        borderLeft: `3px solid ${config.borderColor}`,
        transition: 'opacity 1s ease-in-out',
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Privilege Badge */}
      <div className="privilege-badge" style={{ color: config.color }}>
        <span className="privilege-icon">{config.icon}</span>
        <span className="privilege-label">{config.label}</span>
      </div>

      {/* Message Content */}
      <div className="bubble-content">
        <p>{message.content}</p>
      </div>

      {/* TTL Indicator */}
      <div className={`ttl-indicator ${urgency}`}>
        <div
          className="ttl-bar"
          style={{
            width: `${Math.max(0, (remainingMs / message.ttlMs) * 100)}%`,
            backgroundColor: urgency === 'critical' ? '#DC2626'
              : urgency === 'warning' ? '#D97706'
              : config.color,
          }}
        />
        <span className="ttl-text">{formatRemaining()}</span>
      </div>

      {/* Actions (visible on hover) */}
      {isHovered && !message.preserved && onPreserve && (
        <div className="bubble-actions">
          <button
            className="preserve-btn"
            onClick={() => onPreserve(message.id)}
            title="Preserve this message (disable auto-evaporation)"
          >
            📌 Preserve
          </button>
        </div>
      )}

      {/* Evaporation Warning */}
      {urgency === 'critical' && !message.preserved && (
        <div className="evaporation-warning">
          ⚠️ This message will evaporate in {formatRemaining()}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Styles (CSS-in-JS for component encapsulation)
// ============================================================================

export const evaporatingChatStyles = `
.evaporating-bubble {
  position: relative;
  padding: 12px 16px;
  margin: 8px 0;
  border-radius: 12px;
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  max-width: 80%;
  animation: bubbleAppear 0.3s ease-out;
}

.evaporating-bubble.user {
  margin-left: auto;
  border-radius: 12px 12px 4px 12px;
}

.evaporating-bubble.assistant {
  margin-right: auto;
  border-radius: 12px 12px 12px 4px;
}

.evaporating-bubble.critical {
  animation: criticalPulse 2s ease-in-out infinite;
}

.privilege-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 6px;
  opacity: 0.8;
}

.privilege-icon {
  font-size: 12px;
}

.bubble-content {
  color: #1F2937;
}

.bubble-content p {
  margin: 0;
}

.ttl-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  height: 16px;
}

.ttl-bar {
  flex: 1;
  height: 2px;
  border-radius: 1px;
  transition: width 1s linear, background-color 0.5s ease;
}

.ttl-text {
  font-size: 10px;
  color: #9CA3AF;
  font-variant-numeric: tabular-nums;
  min-width: 60px;
  text-align: right;
}

.ttl-indicator.critical .ttl-text {
  color: #DC2626;
  font-weight: 600;
}

.ttl-indicator.warning .ttl-text {
  color: #D97706;
}

.bubble-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  animation: fadeIn 0.2s ease-out;
}

.preserve-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preserve-btn:hover {
  background: #F3F4F6;
  border-color: #D1D5DB;
}

.evaporation-warning {
  margin-top: 6px;
  padding: 4px 8px;
  background: rgba(220, 38, 38, 0.06);
  border-radius: 4px;
  font-size: 11px;
  color: #DC2626;
  text-align: center;
}

.evaporating-bubble.preserved {
  border-left-width: 4px;
}

.evaporating-bubble.preserved::after {
  content: '📌';
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 14px;
}

@keyframes bubbleAppear {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes criticalPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
  50% { box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.1); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
`;

export default EvaporatingChatBubble;
