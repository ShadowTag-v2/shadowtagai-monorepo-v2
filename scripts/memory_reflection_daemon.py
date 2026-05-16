#!/usr/bin/env python3
"""scripts/memory_reflection_daemon.py — Continuous Agentic Memory.

4-stage loop: Execution → Reflection → Storage → Injection
Watches beads trail, extracts preferences, builds knowledge graph.

Usage:
    python3 scripts/memory_reflection_daemon.py --stats
    python3 scripts/memory_reflection_daemon.py --inject
    python3 scripts/memory_reflection_daemon.py --reflect
    python3 scripts/memory_reflection_daemon.py --graph
    python3 scripts/memory_reflection_daemon.py --watch
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
MEMORY = REPO / ".ai-memory.md"
BEADS = REPO / ".beads" / "issues.jsonl"
KI = Path.home() / ".gemini/antigravity/knowledge"
RLOG = REPO / "data/memory/reflections.jsonl"
GRAPH = REPO / "data/memory/knowledge_graph.json"
RLOG.parent.mkdir(parents=True, exist_ok=True)

def load_memory(): return MEMORY.read_text("utf-8") if MEMORY.exists() else ""
def load_beads():
    if not BEADS.exists(): return []
    out = []
    for ln in BEADS.open(encoding="utf-8"):
        try: out.append(json.loads(ln.strip()))
        except: pass
    return out

def extract_prefs(text):
    prefs = []
    ts = datetime.now(timezone.utc).isoformat()
    for m in re.finditer(r"(?:prefers?|use|always use)\s+(\w[\w\s.]+?)\s+(?:over|instead of)\s+(\w[\w\s.]+)", text, re.I):
        prefs.append({"type":"preference","preferred":m.group(1).strip(),"rejected":m.group(2).strip(),"ts":ts})
    for m in re.finditer(r"(?:never|banned?|prohibited?)\s+(?:use\s+)?(\w[\w\s.]+?)(?:\s*[.;,!])", text, re.I):
        prefs.append({"type":"prohibition","item":m.group(1).strip(),"ts":ts})
    return prefs

def build_graph(prefs):
    g = {"nodes":{},"edges":[],"meta":{"ts":datetime.now(timezone.utc).isoformat(),"count":len(prefs)}}
    for p in prefs:
        if p["type"]=="preference":
            a,b = hashlib.md5(p["preferred"].encode()).hexdigest()[:8], hashlib.md5(p["rejected"].encode()).hexdigest()[:8]
            g["nodes"][a]={"label":p["preferred"],"status":"preferred"}
            g["nodes"][b]={"label":p["rejected"],"status":"rejected"}
            g["edges"].append({"from":a,"to":b,"rel":"preferred_over"})
        elif p["type"]=="prohibition":
            h = hashlib.md5(p["item"].encode()).hexdigest()[:8]
            g["nodes"][h]={"label":p["item"],"status":"banned"}
    return g

def inject_prompt():
    mem = load_memory()
    if not mem: return "No persistent memory."
    parts = ["<persistent_memory>","Facts from previous sessions:"]
    for ln in mem.split("\n"):
        if ln.strip().startswith("- "): parts.append(ln.strip())
    parts.append("</persistent_memory>")
    return "\n".join(parts)

def reflect():
    prefs = []
    for b in load_beads()[-50:]: prefs.extend(extract_prefs(json.dumps(b)))
    prefs.extend(extract_prefs(load_memory()))
    return prefs

def log_ref(refs):
    with RLOG.open("a", encoding="utf-8") as f:
        for r in refs: f.write(json.dumps(r)+"\n")

def stats():
    mem = load_memory()
    rc = sum(1 for _ in RLOG.open(encoding="utf-8")) if RLOG.exists() else 0
    ki = sum(1 for d in KI.iterdir() if d.is_dir() and not d.name.startswith("_")) if KI.exists() else 0
    gn=ge=0
    if GRAPH.exists():
        g=json.loads(GRAPH.read_text()); gn=len(g.get("nodes",{})); ge=len(g.get("edges",[]))
    print(f"{'═'*60}\n  AGENTIC MEMORY — Stats\n{'═'*60}")
    print(f"  Facts: {mem.count(chr(10)+'- ')} | Beads: {len(load_beads())} | Reflections: {rc}")
    print(f"  KIs: {ki} | Graph: {gn} nodes, {ge} edges | Size: {len(mem):,}B\n{'═'*60}")

def watch(interval=300):
    print(f"[DAEMON] Memory reflection (interval={interval}s)")
    last = len(load_beads())
    while True:
        try:
            cur = load_beads()
            if len(cur) > last:
                prefs = []
                for b in cur[last:]: prefs.extend(extract_prefs(json.dumps(b)))
                if prefs: log_ref(prefs)
                g = build_graph(prefs); GRAPH.write_text(json.dumps(g,indent=2))
                last = len(cur)
                print(f"[DAEMON] +{len(prefs)} prefs, {len(g['nodes'])} nodes")
            time.sleep(interval)
        except KeyboardInterrupt: break
        except Exception as e: print(f"[ERR] {e}",file=sys.stderr); time.sleep(interval)

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--watch",action="store_true"); p.add_argument("--inject",action="store_true")
    p.add_argument("--stats",action="store_true"); p.add_argument("--reflect",action="store_true")
    p.add_argument("--graph",action="store_true"); p.add_argument("--interval",type=int,default=300)
    a = p.parse_args()
    if a.stats: stats()
    elif a.inject: print(inject_prompt())
    elif a.watch: watch(a.interval)
    elif a.graph:
        r=reflect(); g=build_graph(r); GRAPH.write_text(json.dumps(g,indent=2))
        print(f"Graph: {len(g['nodes'])} nodes, {len(g['edges'])} edges → {GRAPH}")
    elif a.reflect: r=reflect(); log_ref(r); print(f"Reflected: {len(r)} prefs")
    else: reflect(); stats()
