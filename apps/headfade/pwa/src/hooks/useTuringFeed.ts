'use client';
/**
 * useTuringFeed — Cognitive Lock State Machine
 *
 * Encapsulates the full HeadFade "Turing Feed" loop:
 *   1. Video loops infinitely until a vote is cast.
 *   2. Vote triggers a Green/Correct or Red/Incorrect reveal flash.
 *   3. 800ms after the flash, if autoScroll is ON, advances to the next item.
 *   4. autoScroll can be toggled OFF by the user (TikTok-mode manual swipe).
 *   5. Adaptive preference signal emitted per vote for the recommendation engine.
 *
 * AUTH: If no userSession is present, onVote is a no-op and the auth wall
 * must be raised by the parent. This hook does NOT show UI directly.
 */

import { useCallback, useRef, useState } from 'react';

export type RevealState = 'correct' | 'incorrect' | null;

export interface TuringFeedOptions {
  /** Total items in the queue */
  count: number;
  /** Called when the user attempts a vote. Returns true if vote was accepted. */
  onVoteAccepted: (index: number, choice: 'ai' | 'human') => void;
  /** Emitted on every transition so the parent can scroll the DOM */
  onAdvance: (nextIndex: number) => void;
  /** True if the current user is authenticated */
  isAuthenticated: boolean;
  /** Called when an unauthenticated user attempts to vote */
  onAuthRequired: () => void;
}

export interface TuringFeedState {
  currentIndex: number;
  autoScroll: boolean;
  revealState: RevealState; // null = no reveal, 'correct' | 'incorrect' = flashing
  setAutoScroll: (v: boolean) => void;
  handleVote: (choice: 'ai' | 'human', actualType: 'ai' | 'human') => void;
  goToIndex: (i: number) => void;
}

/** Delay (ms) between reveal flash and auto-advance. */
const REVEAL_DURATION_MS = 800;

export function useTuringFeed({
  count,
  onVoteAccepted,
  onAdvance,
  isAuthenticated,
  onAuthRequired,
}: TuringFeedOptions): TuringFeedState {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [autoScroll, setAutoScrollRaw] = useState<boolean>(() => {
    try {
      const stored =
        typeof window !== 'undefined' ? localStorage.getItem('headfade_autoscroll_v1') : null;
      return stored !== null ? (JSON.parse(stored) as boolean) : true;
    } catch {
      return true;
    }
  });
  const [revealState, setRevealState] = useState<RevealState>(null);
  const advanceTimerRef = useRef<ReturnType<typeof setTimeout>>();

  const setAutoScroll = useCallback((v: boolean) => {
    setAutoScrollRaw(v);
    // Persist preference across page refreshes
    try {
      localStorage.setItem('headfade_autoscroll_v1', JSON.stringify(v));
    } catch {
      /* quota */
    }
  }, []);

  const goToIndex = useCallback(
    (i: number) => {
      const next = Math.min(i, count - 1);
      setCurrentIndex(next);
      onAdvance(next);
    },
    [count, onAdvance],
  );

  const handleVote = useCallback(
    (choice: 'ai' | 'human', actualType: 'ai' | 'human') => {
      if (!isAuthenticated) {
        onAuthRequired();
        return;
      }

      // Clear any pending advance
      clearTimeout(advanceTimerRef.current);

      const isCorrect = choice === actualType;
      setRevealState(isCorrect ? 'correct' : 'incorrect');
      onVoteAccepted(currentIndex, choice);

      // After reveal, clear flash and optionally advance
      advanceTimerRef.current = setTimeout(() => {
        setRevealState(null);
        if (autoScroll) {
          goToIndex(currentIndex + 1);
        }
      }, REVEAL_DURATION_MS);
    },
    [isAuthenticated, onAuthRequired, currentIndex, autoScroll, goToIndex, onVoteAccepted],
  );

  return { currentIndex, autoScroll, revealState, setAutoScroll, handleVote, goToIndex };
}
