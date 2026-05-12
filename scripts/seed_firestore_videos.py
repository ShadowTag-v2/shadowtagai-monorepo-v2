#!/usr/bin/env python3
"""
HeadFade Firestore Seed Script
Populates /videos/video_0..19 and /meta/vote_totals
matching the deterministic seedVotes() logic in useVotes.ts.

Usage:
  GOOGLE_CLOUD_PROJECT=shadowtag-omega-v4 python3 scripts/seed_firestore_videos.py
"""

import math
import os
import sys

try:
  import firebase_admin
  from firebase_admin import credentials, firestore
except ImportError:
  print(
    "ERROR: firebase-admin not installed. Run: pip install firebase-admin",
    file=sys.stderr,
  )
  sys.exit(1)

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")


# Mirror of useVotes.ts seedVotes(i)
def seed_votes(i: int) -> dict:
  base = 1200 + i * 337 + math.floor(math.sin(i) * 800)
  p = 0.35 + (i % 7) * 0.08
  return {
    "voteAI": math.floor(base * p),
    "voteHuman": math.floor(base * (1 - p)),
  }



SEED_VIDEOS = [
  {
    "title": "How AI Is Changing Music Creation Forever",
    "author": "TechVision",
    "views": "2.4M",
  },
  {
    "title": "I Built a House Using Only AI Blueprints",
    "author": "Builder Mike",
    "views": "1.8M",
  },
  {"title": "The Science Behind Viral Videos", "author": "Veritasium", "views": "4.1M"},
  {
    "title": "Perfect Sourdough in Under 4 Hours",
    "author": "Joshua Weissman",
    "views": "890K",
  },
  {"title": "Why Studios Now Use AI Actors", "author": "Film Theory", "views": "3.2M"},
  {
    "title": "Day in My Life: Remote Dev in Tokyo",
    "author": "Joma Tech",
    "views": "1.5M",
  },
  {
    "title": "Biggest Startup Mistakes to Avoid",
    "author": "Graham Stephan",
    "views": "2.1M",
  },
  {"title": "We Tested 50 AI Image Generators", "author": "MKBHD", "views": "5.7M"},
  {
    "title": "How to Actually Get Good at Chess",
    "author": "GothamChess",
    "views": "1.3M",
  },
  {
    "title": "I Survived 100 Days in an AI Minecraft World",
    "author": "Luke TheNotable",
    "views": "8.9M",
  },
  {
    "title": "Living on $1/Day in Different Countries",
    "author": "Nas Daily",
    "views": "6.2M",
  },
  {
    "title": "Why Airlines Are Getting Worse",
    "author": "Wendover Productions",
    "views": "2.8M",
  },
  {
    "title": "10-Minute Full Body Workout — No Equipment",
    "author": "Chloe Ting",
    "views": "14.2M",
  },
  {
    "title": "How This 19-Year-Old Makes $50K/Month AI",
    "author": "Ali Abdaal",
    "views": "3.4M",
  },
  {
    "title": "Every Fast Food Chicken Sandwich Ranked",
    "author": "Good Mythical Morning",
    "views": "4.5M",
  },
  {
    "title": "Learn Python in 1 Hour — 2026 Edition",
    "author": "Programming with Mosh",
    "views": "9.1M",
  },
  {
    "title": "I Let AI Control My Life for 30 Days",
    "author": "Yes Theory",
    "views": "7.3M",
  },
  {
    "title": "The Most Satisfying Machines Ever Made",
    "author": "SmarterEveryDay",
    "views": "11.6M",
  },
  {
    "title": "Gordon Ramsay Reacts to AI Recipes",
    "author": "Gordon Ramsay",
    "views": "15.8M",
  },
  {
    "title": "Why Japan Is 10 Years Ahead of Your City",
    "author": "Abroad in Japan",
    "views": "5.4M",
  },
]


def main() -> None:
  # Initialize with ADC (gcloud auth application-default login)
  if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {"projectId": PROJECT})

  db = firestore.client()
  batch = db.batch()

  total_ai = 0
  total_human = 0

  print(f"Seeding {len(SEED_VIDEOS)} video documents to project '{PROJECT}'...")
  for i, meta in enumerate(SEED_VIDEOS):
    votes = seed_votes(i)
    doc_ref = db.collection("videos").document(f"video_{i}")
    payload = {
      "title": meta["title"],
      "author": meta["author"],
      "views": meta["views"],
      "voteAI": votes["voteAI"],
      "voteHuman": votes["voteHuman"],
      "userVoteByKey": {},
    }
    batch.set(doc_ref, payload, merge=True)
    total_ai += votes["voteAI"]
    total_human += votes["voteHuman"]
    print(
      f"  video_{i}: AI={votes['voteAI']:,}  Human={votes['voteHuman']:,}  → {meta['title'][:50]}"
    )

  # Seed meta/vote_totals only if it doesn't exist yet
  meta_ref = db.collection("meta").document("vote_totals")
  meta_snap = meta_ref.get()
  if not meta_snap.exists:
    batch.set(
      meta_ref,
      {"totalAI": total_ai + 68_200_000, "totalHuman": total_human + 31_800_000},
    )
    print(
      f"\nCreating meta/vote_totals  totalAI={total_ai + 68_200_000:,}  totalHuman={total_human + 31_800_000:,}"
    )
  else:
    print("\nmeta/vote_totals already exists — skipping global counter seed.")

  batch.commit()
  print("\n✅ Firestore seed complete.")


if __name__ == "__main__":
  main()
