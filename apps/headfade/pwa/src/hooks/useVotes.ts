'use client';
import { doc, increment, onSnapshot, runTransaction } from 'firebase/firestore';
import { useCallback, useEffect, useState } from 'react';
import { getFirestoreInstance, getAnalyticsInstance } from '@/lib/firebase';

const LS_KEY = 'headfade_votes_v1';
const LS_FILTER = 'headfade_filter_v1';
const LS_SAVED = 'headfade_saved_v1';

export type VoteChoice = 'ai' | 'human' | null;
export type VoteFilter = 'all' | 'voted-ai' | 'voted-human' | 'unvoted';

export interface VoteState {
  voteAI: number;
  voteHuman: number;
  userVote: VoteChoice;
}

function seedVotes(i: number) {
  const base = 1200 + i * 337 + Math.floor(Math.sin(i) * 800);
  const p = 0.35 + (i % 7) * 0.08;
  return { voteAI: Math.floor(base * p), voteHuman: Math.floor(base * (1 - p)) };
}

function loadLS<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback;
  try {
    return JSON.parse(localStorage.getItem(key) ?? 'null') ?? fallback;
  } catch {
    return fallback;
  }
}

function saveLS(key: string, val: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch {
    /* quota */
  }
}

export function useVotes(count: number) {
  const [votes, setVotes] = useState<Record<string, VoteState>>(() => {
    const saved = loadLS<Record<string, VoteChoice>>(LS_KEY, {});
    const out: Record<string, VoteState> = {};
    for (let i = 0; i < count; i++) {
      const uv = saved[i] ?? null;
      const s = seedVotes(i);
      out[i] = {
        ...s,
        voteAI: s.voteAI + (uv === 'ai' ? 1 : 0),
        voteHuman: s.voteHuman + (uv === 'human' ? 1 : 0),
        userVote: uv,
      };
    }
    return out;
  });

  const [filter, setFilterRaw] = useState<VoteFilter>(() => loadLS(LS_FILTER, 'all'));
  const [saved, setSaved] = useState<Set<string>>(() => new Set(loadLS<string[]>(LS_SAVED, [])));
  const [globalAI, setGlobalAI] = useState(68_200_000);
  const [globalHuman, setGlobalHuman] = useState(31_800_000);

  // Live global totals from Firestore — async init to avoid undefined db
  useEffect(() => {
    let unsub: (() => void) | undefined;
    let cancelled = false;
    getFirestoreInstance().then((db) => {
      if (cancelled) return;
      const ref = doc(db, 'meta', 'vote_totals');
      unsub = onSnapshot(ref, (snap) => {
        if (!snap.exists()) return;
        const d = snap.data();
        if (d.totalAI) setGlobalAI(d.totalAI);
        if (d.totalHuman) setGlobalHuman(d.totalHuman);
      });
    }).catch(() => { /* offline */ });
    return () => {
      cancelled = true;
      unsub?.();
    };
  }, []);

  const setFilter = useCallback((f: VoteFilter) => {
    setFilterRaw(f);
    saveLS(LS_FILTER, f);
  }, []);

  const toggleSave = useCallback((id: string) => {
    setSaved((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      saveLS(LS_SAVED, Array.from(next));
      return next;
    });
  }, []);

  const vote = useCallback(async (key: string, choice: VoteChoice) => {
    if (!choice) return;
    setVotes((prev) => {
      const cur = prev[key];
      if (!cur || cur.userVote === choice) return prev;
      const old = cur.userVote;
      return {
        ...prev,
        [key]: {
          voteAI: cur.voteAI + (choice === 'ai' ? 1 : 0) - (old === 'ai' ? 1 : 0),
          voteHuman: cur.voteHuman + (choice === 'human' ? 1 : 0) - (old === 'human' ? 1 : 0),
          userVote: choice,
        },
      };
    });

    // Persist user choice
    const allChoices = loadLS<Record<string, VoteChoice>>(LS_KEY, {});
    allChoices[key] = choice;
    saveLS(LS_KEY, allChoices);

    // Firestore atomic increment
    try {
      const db = await getFirestoreInstance();
      const ref = doc(db, 'videos', `video_${key}`);
      await runTransaction(db, async (tx) => {
        const snap = await tx.get(ref);
        const old = snap.data()?.userVoteByKey?.[key] ?? null;
        const updates: Record<string, unknown> = { [`userVoteByKey.${key}`]: choice };
        if (choice === 'ai') updates.voteAI = increment(1);
        else updates.voteHuman = increment(1);
        if (old === 'ai') updates.voteAI = increment(-1);
        if (old === 'human') updates.voteHuman = increment(-1);
        tx.set(ref, updates, { merge: true });
      });
      // Global totals
      const metaRef = doc(db, 'meta', 'vote_totals');
      await runTransaction(db, async (tx) => {
        const updates: Record<string, unknown> = {};
        if (choice === 'ai') updates.totalAI = increment(1);
        else updates.totalHuman = increment(1);
        tx.set(metaRef, updates, { merge: true });
      });
    } catch {
      /* offline — local state still correct */
    }

    // Analytics — dynamic import; null until first interaction triggers init
    const analytics = getAnalyticsInstance();
    if (analytics) {
      import('firebase/analytics').then(({ logEvent: log }) => {
        log(analytics, 'vote_cast', { choice, videoId: key });
      });
    }
  }, []);

  return { votes, vote, filter, setFilter, saved, toggleSave, globalAI, globalHuman };
}
