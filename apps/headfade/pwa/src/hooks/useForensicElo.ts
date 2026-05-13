'use client';

/**
 * useForensicElo — Dual Reward Economy
 *
 * VOTER SIDE — "Forensic Elo"
 * ───────────────────────────
 * Every vote earns or costs Elo points. The delta is dynamic:
 *   - Spotting an obvious fake (fooled <20% of platform): +1
 *   - Spotting a realistic fake (fooled 50–75%):          +15
 *   - Spotting a god-tier fake (fooled >90%):             +50
 *   - Missing an obvious fake (you guessed wrong when everyone was right): −5
 *
 * CREATOR SIDE — "Deception Dividend"
 * ─────────────────────────────────────
 * Creator score is their video's fool-rate across all authenticated voters.
 * Fool Rate Tiers:
 *   < 25%  — "Transparent"  (no bonus)
 *   25–50% — "Convincing"   (1× base price)
 *   50–75% — "Expert"       (2× price multiplier)
 *   > 75%  — "God-Tier"     (Dynamic Pricing unlocked: up to 6× multiplier)
 *
 * Firestore schema (per user doc `users/{uid}`):
 *   { eloRating: number, totalVotes: number, correctVotes: number, badges: string[] }
 *
 * Firestore schema (per video doc `videos/{videoId}`):
 *   { creatorUid: string, totalVoters: number, aiVotes: number, humanVotes: number,
 *     foolRate: number, deceptionTier: string, dynamicPriceMultiplier: number }
 */

import { doc, increment, onSnapshot, runTransaction } from 'firebase/firestore';
import { useCallback, useEffect, useState } from 'react';
import { getFirestoreInstance } from '@/lib/firebase';

export type DeceptionTier = 'transparent' | 'convincing' | 'expert' | 'god-tier';

export interface ForensicEloState {
  eloRating: number;
  correctVotes: number;
  totalVotes: number;
  badges: string[];
  accuracy: number; // 0–100 %
}

export interface CreatorStats {
  foolRate: number; // 0–1
  tier: DeceptionTier;
  priceMultiplier: number;
}

/** Compute Elo delta based on how many people this video fooled (0–1). */
function eloGain(foolRate: number, isCorrect: boolean): number {
  if (!isCorrect) return foolRate < 0.2 ? -5 : -2;
  if (foolRate > 0.9) return 50;
  if (foolRate > 0.75) return 25;
  if (foolRate > 0.5) return 15;
  if (foolRate > 0.25) return 5;
  return 1;
}

function deceptionTier(foolRate: number): DeceptionTier {
  if (foolRate > 0.75) return 'god-tier';
  if (foolRate > 0.5) return 'expert';
  if (foolRate > 0.25) return 'convincing';
  return 'transparent';
}

function priceMultiplier(tier: DeceptionTier): number {
  switch (tier) {
    case 'god-tier':
      return 6;
    case 'expert':
      return 2;
    case 'convincing':
      return 1;
    default:
      return 0.5;
  }
}

const LS_ELO_KEY = 'headfade_elo_v1';

function loadLocalElo(): ForensicEloState {
  if (typeof window === 'undefined')
    return { eloRating: 1000, correctVotes: 0, totalVotes: 0, badges: [], accuracy: 0 };
  try {
    return (
      JSON.parse(localStorage.getItem(LS_ELO_KEY) ?? 'null') ?? {
        eloRating: 1000,
        correctVotes: 0,
        totalVotes: 0,
        badges: [],
        accuracy: 0,
      }
    );
  } catch {
    return { eloRating: 1000, correctVotes: 0, totalVotes: 0, badges: [], accuracy: 0 };
  }
}

export function useForensicElo(uid: string | null) {
  const [elo, setElo] = useState<ForensicEloState>(loadLocalElo);

  // Subscribe to live Firestore Elo when authenticated — async init
  useEffect(() => {
    if (!uid) return;
    let unsub: (() => void) | undefined;
    let cancelled = false;
    getFirestoreInstance().then((db) => {
      if (cancelled) return;
      const ref = doc(db, 'users', uid);
      unsub = onSnapshot(ref, (snap) => {
        if (!snap.exists()) return;
        const d = snap.data();
        const next: ForensicEloState = {
          eloRating: d.eloRating ?? 1000,
          correctVotes: d.correctVotes ?? 0,
          totalVotes: d.totalVotes ?? 0,
          badges: d.badges ?? [],
          accuracy: d.totalVotes > 0 ? Math.round((d.correctVotes / d.totalVotes) * 100) : 0,
        };
        setElo(next);
        try {
          localStorage.setItem(LS_ELO_KEY, JSON.stringify(next));
        } catch {
          /* quota */
        }
      });
    }).catch(() => { /* offline */ });
    return () => {
      cancelled = true;
      unsub?.();
    };
  }, [uid]);

  /**
   * Called immediately after a confirmed vote to update Elo optimistically
   * and write to Firestore atomically.
   */
  const recordVoteOutcome = useCallback(
    async (videoId: string, isCorrect: boolean, foolRate: number) => {
      const delta = eloGain(foolRate, isCorrect);

      // Optimistic local update
      setElo((prev) => {
        const next = {
          ...prev,
          eloRating: Math.max(0, prev.eloRating + delta),
          totalVotes: prev.totalVotes + 1,
          correctVotes: prev.correctVotes + (isCorrect ? 1 : 0),
          accuracy: Math.round(
            ((prev.correctVotes + (isCorrect ? 1 : 0)) / (prev.totalVotes + 1)) * 100,
          ),
        };
        // Badge unlock: top detection milestones
        const badges = [...prev.badges];
        if (next.correctVotes === 10 && !badges.includes('🎯 First Blood'))
          badges.push('🎯 First Blood');
        if (next.eloRating >= 1200 && !badges.includes('🔬 Forensics Analyst'))
          badges.push('🔬 Forensics Analyst');
        if (next.eloRating >= 1500 && !badges.includes('🏅 OSINT Verified'))
          badges.push('🏅 OSINT Verified');
        if (next.eloRating >= 2000 && !badges.includes('💎 God-Tier Detector'))
          badges.push('💎 God-Tier Detector');
        next.badges = badges;
        try {
          localStorage.setItem(LS_ELO_KEY, JSON.stringify(next));
        } catch {
          /* quota */
        }
        return next;
      });

      if (!uid) return;

      // Firestore write — read-then-write to ensure 1000 base Elo for new users
      try {
        const db = await getFirestoreInstance();
        const userRef = doc(db, 'users', uid);
        await runTransaction(db, async (tx) => {
          const snap = await tx.get(userRef);
          if (!snap.exists() || snap.data()?.eloRating === undefined) {
            // First vote ever — initialize with base 1000
            tx.set(
              userRef,
              {
                eloRating: 1000 + delta,
                totalVotes: 1,
                correctVotes: isCorrect ? 1 : 0,
              },
              { merge: true },
            );
          } else {
            tx.set(
              userRef,
              {
                eloRating: increment(delta),
                totalVotes: increment(1),
                correctVotes: increment(isCorrect ? 1 : 0),
              },
              { merge: true },
            );
          }
        });

        // Update video creator stats
        const videoRef = doc(db, 'videos', videoId);
        await runTransaction(db, async (tx) => {
          const snap = await tx.get(videoRef);
          const d = snap.data() ?? {};
          const totalVoters = (d.totalVoters ?? 0) + 1;
          const aiVotes = (d.aiVotes ?? 0) + (!isCorrect ? 1 : 0); // wrong votes = thought it was AI when human or vice-versa
          const newFoolRate = totalVoters > 0 ? aiVotes / totalVoters : 0;
          const tier = deceptionTier(newFoolRate);
          tx.set(
            videoRef,
            {
              totalVoters: increment(1),
              foolRate: newFoolRate,
              deceptionTier: tier,
              dynamicPriceMultiplier: priceMultiplier(tier),
            },
            { merge: true },
          );
        });
      } catch {
        /* offline */
      }
    },
    [uid],
  );

  return { elo, recordVoteOutcome };
}

