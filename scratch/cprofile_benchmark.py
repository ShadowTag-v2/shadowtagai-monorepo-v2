import asyncio
import cProfile
import pstats
from pathlib import Path
import sys

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))
from tool_gateway.async_evidence import AsyncEvidenceLogger


async def run_1000_ops(logger):
    ops = []
    for i in range(1000):
        ops.append(logger.log_execution(f"tool-{i}", success=True, detail=f"concurrent entry {i}"))
    await asyncio.gather(*ops)


def main():
    tmp_dir = Path("/tmp/beads_benchmark")
    tmp_dir.mkdir(exist_ok=True)
    logger = AsyncEvidenceLogger(tmp_dir)

    profiler = cProfile.Profile()
    profiler.enable()

    asyncio.run(run_1000_ops(logger))

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(20)


if __name__ == "__main__":
    main()
