import { useCallback, useEffect, useState } from 'react';

/**
 * useForensicElo manages the user's forensic ELO rating.
 * It tracks how well the user detects AI-generated content.
 */
export function useForensicElo() {
  const [elo, setElo] = useState<number>(1200);

  // Load ELO from localStorage on mount
  useEffect(() => {
    const savedElo = localStorage.getItem('headfade_forensic_elo');
    if (savedElo) {
      const parsed = parseInt(savedElo, 10);
      if (!Number.isNaN(parsed)) {
        setElo(parsed);
      }
    }
  }, []);

  /**
   * recordVoteOutcome updates the forensic ELO based on whether the user was correct.
   */
  const recordVoteOutcome = useCallback((wasCorrect: boolean) => {
    setElo((currentElo) => {
      const kFactor = 32;
      const actualScore = wasCorrect ? 1 : 0;
      const expectedScore = 0.5; // Simplified ELO: assume 50/50 chance

      const newElo = Math.round(currentElo + kFactor * (actualScore - expectedScore));

      localStorage.setItem('headfade_forensic_elo', newElo.toString());
      return newElo;
    });
  }, []);

  return {
    elo,
    recordVoteOutcome,
  };
}
