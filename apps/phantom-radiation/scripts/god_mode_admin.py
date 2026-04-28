# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import json
import logging
import os
import shlex
import signal

# Ensure project root is importable when launched as `python3 scripts/god_mode_admin.py`.
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.steel.artifact_api import ArtifactAPI
from libs.steel.retrieve_memory import SovereignMemoryRetriever
from libs.steel.sdk import VelocityEngine
from libs.steel.vfs import ShadowVFS
from libs.steel.write_memory import SovereignMemoryPool

from libs.steel.sentinel import JudgeSixSentinel
import contextlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("GodModeAdmin")


@dataclass
class AdminTask:
    task_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: float = field(default_factory=time.time)


class GodModeRuntime:
    def __init__(self):
        self.project_id = os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
        self.workspace_root = os.environ.get(
            "GOD_MODE_WORKSPACE",
            "/Users/pikeymickey/.gemini/antigravity/playground/phantom-radiation",
        )
        self.bucket_name = os.environ.get("GOD_MODE_BUCKET", f"{self.project_id}-godmode-artifacts")

        self.queue: asyncio.Queue[AdminTask] = asyncio.Queue()
        self.stop_event = asyncio.Event()
        self.history: list[dict[str, Any]] = []

        self.sentinel = JudgeSixSentinel()
        self.vfs = ShadowVFS(root_dir=self.workspace_root)
        self.engine = VelocityEngine(
            agent_name="Admin_GodMode",
            auto_apply=True,
            sentinel=self.sentinel,
            vfs=self.vfs,
            workspace_root=self.workspace_root,
        )
        self.artifacts = ArtifactAPI(project_id=self.project_id, bucket_name=self.bucket_name)
        self.swarm = None

        self.schedules: list[dict[str, Any]] = [
            {
                "name": "sync_repo",
                "interval_sec": int(os.environ.get("GOD_MODE_SYNC_INTERVAL_SEC", "600")),
                "last_run": 0.0,
                "task": AdminTask(task_type="pull_updates"),
            },
            {
                "name": "health_snapshot",
                "interval_sec": int(os.environ.get("GOD_MODE_HEALTH_INTERVAL_SEC", "120")),
                "last_run": 0.0,
                "task": AdminTask(task_type="status"),
            },
        ]

    async def enqueue(self, task: AdminTask) -> None:
        await self.queue.put(task)
        logger.info("📥 QUEUED %s (%s)", task.task_type, task.task_id)

    async def run(self) -> None:
        logger.info("==========================================")
        logger.info("   ☢️  SHADOWTAG OMEGA V7: LIVE ENGINE")
        logger.info("==========================================")
        logger.info("⚡ Initializing Velocity Engine...")
        logger.info("✅ Engine Ready.")
        logger.info("🎮 Awaiting Command Flux...")

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(
                    sig,
                    lambda: asyncio.create_task(self.enqueue(AdminTask(task_type="shutdown"))),
                )

        workers = [asyncio.create_task(self.worker(i)) for i in range(3)]
        scheduler = asyncio.create_task(self.scheduler_loop())
        shell = asyncio.create_task(self.command_loop())

        await self.stop_event.wait()
        shell.cancel()
        scheduler.cancel()
        for worker in workers:
            worker.cancel()

        await asyncio.gather(shell, scheduler, *workers, return_exceptions=True)
        logger.info("🛑 Engine Powering Down.")

    async def worker(self, worker_id: int) -> None:
        while True:
            task = await self.queue.get()
            started = time.time()
            status = "ok"
            output = ""
            try:
                output = await self.execute(task)
            except Exception as exc:
                status = "error"
                output = f"{type(exc).__name__}: {exc}"
                logger.exception("Worker %s failed task %s", worker_id, task.task_id)
            finally:
                elapsed = round(time.time() - started, 3)
                self.history.append(
                    {
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "status": status,
                        "elapsed_sec": elapsed,
                        "output": output[:1000],
                    },
                )
                if len(self.history) > 200:
                    self.history = self.history[-200:]
                logger.info(
                    "✅ WORKER-%s %s (%s) in %ss\n%s",
                    worker_id,
                    task.task_type,
                    task.task_id,
                    elapsed,
                    output[:800] or "(no output)",
                )
                self.queue.task_done()

    async def scheduler_loop(self) -> None:
        while not self.stop_event.is_set():
            now = time.time()
            for scheduled in self.schedules:
                if now - scheduled["last_run"] >= scheduled["interval_sec"]:
                    template: AdminTask = scheduled["task"]
                    await self.enqueue(
                        AdminTask(task_type=template.task_type, payload=template.payload),
                    )
                    scheduled["last_run"] = now
            await asyncio.sleep(1.0)

    async def execute(self, task: AdminTask) -> str:
        task_type = task.task_type
        payload = task.payload

        if task_type == "shell":
            cmd = payload.get("command", "")
            allow_unsafe = bool(payload.get("allow_unsafe", False))
            return self.engine.run_shell(cmd, allow_unsafe=allow_unsafe)

        if task_type == "write_file":
            path = payload["path"]
            content = payload.get("content", "")
            use_shadow = bool(payload.get("use_shadow", True))
            commit = bool(payload.get("commit", False))
            return self.engine.write_file(path, content, use_shadow=use_shadow, commit=commit)

        if task_type == "commit_shadow":
            return self.engine.commit_shadow()

        if task_type == "rollback_shadow":
            return self.engine.rollback_shadow()

        if task_type == "pull_updates":
            return "✅ sync complete" if self.engine.pull_updates() else "❌ sync failed"

        if task_type == "swarm_mission":
            recon_url = payload["recon_url"]
            executive_task = payload["executive_task"]
            if self.swarm is None:
                from libs.steel.swarm import SwarmOrchestrator

                self.swarm = SwarmOrchestrator()
            result = await self.swarm.run_parallel_mission(
                recon_url=recon_url,
                executive_task=executive_task,
            )
            return json.dumps(result, default=str)[:3000]

        if task_type == "memory_write":
            memory_id = await SovereignMemoryPool.write_memory(
                domain=payload.get("domain", "general"),
                thought_text=payload["thought_text"],
                metadata=payload.get("metadata", {}),
            )
            return f"🧠 memory_id={memory_id}"

        if task_type == "memory_search":
            results = await SovereignMemoryRetriever.search_memory(
                query_text=payload["query_text"],
                limit=int(payload.get("limit", 5)),
                domain_filter=payload.get("domain_filter"),
            )
            return json.dumps(results, default=str)[:4000]

        if task_type == "artifact_upload":
            name = payload["name"]
            data = payload["data"]
            metadata = payload.get("metadata", {})
            uploaded = self.artifacts.upload_artifact(name=name, data=data, metadata=metadata)
            indexed = self.artifacts.index_in_bigquery(artifact_id=name, metadata=metadata)
            return f"📦 uploaded={uploaded} indexed={indexed}"

        if task_type == "status":
            summary = {
                "queue_size": self.queue.qsize(),
                "history_size": len(self.history),
                "project_id": self.project_id,
                "workspace_root": self.workspace_root,
                "scheduler_jobs": [
                    {
                        "name": s["name"],
                        "interval_sec": s["interval_sec"],
                    }
                    for s in self.schedules
                ],
            }
            return json.dumps(summary)

        if task_type == "shutdown":
            self.stop_event.set()
            return "🛑 Shutdown signal received."

        return f"❌ Unknown task type: {task_type}"

    async def command_loop(self) -> None:
        self._print_help()
        while not self.stop_event.is_set():
            line = await asyncio.to_thread(input, "god-mode> ")
            command = line.strip()
            if not command:
                continue
            if command in {"quit", "exit", "stop"}:
                await self.enqueue(AdminTask(task_type="shutdown"))
                continue
            if command == "help":
                self._print_help()
                continue
            if command == "status":
                await self.enqueue(AdminTask(task_type="status"))
                continue
            if command == "sync":
                await self.enqueue(AdminTask(task_type="pull_updates"))
                continue
            if command == "commit":
                await self.enqueue(AdminTask(task_type="commit_shadow"))
                continue
            if command == "rollback":
                await self.enqueue(AdminTask(task_type="rollback_shadow"))
                continue
            if command.startswith("shell "):
                await self.enqueue(
                    AdminTask(task_type="shell", payload={"command": command[6:].strip()}),
                )
                continue
            if command.startswith("write "):
                # write <path> <content>
                try:
                    parts = shlex.split(command)
                    path = parts[1]
                    content = " ".join(parts[2:])
                    await self.enqueue(
                        AdminTask(
                            task_type="write_file",
                            payload={"path": path, "content": content, "use_shadow": True},
                        ),
                    )
                except Exception:
                    logger.error("Usage: write <path> <content>")
                continue
            if command.startswith("mission "):
                # mission <url> | <executive_task>
                body = command[len("mission ") :]
                if "|" not in body:
                    logger.error("Usage: mission <url> | <executive_task>")
                    continue
                recon_url, executive_task = [s.strip() for s in body.split("|", 1)]
                await self.enqueue(
                    AdminTask(
                        task_type="swarm_mission",
                        payload={"recon_url": recon_url, "executive_task": executive_task},
                    ),
                )
                continue
            if command.startswith("memw "):
                # memw <domain> | <thought_text>
                body = command[len("memw ") :]
                if "|" not in body:
                    logger.error("Usage: memw <domain> | <thought_text>")
                    continue
                domain, thought_text = [s.strip() for s in body.split("|", 1)]
                await self.enqueue(
                    AdminTask(
                        task_type="memory_write",
                        payload={"domain": domain, "thought_text": thought_text},
                    ),
                )
                continue
            if command.startswith("mems "):
                query_text = command[len("mems ") :].strip()
                await self.enqueue(
                    AdminTask(task_type="memory_search", payload={"query_text": query_text}),
                )
                continue
            if command.startswith("artifact "):
                # artifact <name> | <data>
                body = command[len("artifact ") :]
                if "|" not in body:
                    logger.error("Usage: artifact <name> | <data>")
                    continue
                name, data = [s.strip() for s in body.split("|", 1)]
                await self.enqueue(
                    AdminTask(task_type="artifact_upload", payload={"name": name, "data": data}),
                )
                continue
            if command.startswith("json "):
                try:
                    obj = json.loads(command[len("json ") :])
                    await self.enqueue(
                        AdminTask(task_type=obj["type"], payload=obj.get("payload", {})),
                    )
                except Exception as exc:
                    logger.error("json parse failed: %s", exc)
                continue

            logger.error("Unknown command. Type 'help'.")

    def _print_help(self) -> None:
        logger.info(
            "Commands: help | status | sync | shell <cmd> | write <path> <content> | "
            "mission <url> | <task> | memw <domain> | <text> | mems <query> | "
            "artifact <name> | <data> | commit | rollback | json <task-json> | stop",
        )


def main() -> None:
    runtime = GodModeRuntime()
    asyncio.run(runtime.run())


if __name__ == "__main__":
    main()
