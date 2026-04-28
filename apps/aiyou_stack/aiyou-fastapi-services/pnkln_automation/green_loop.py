# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess

from google.cloud import aiplatform as v

MODEL_ID = os.getenv("PNKLN_VERTEX_MODEL", "text-bison@001")
MAX_ITERS = int(os.getenv("PNKLN_GL_MAX_ITERS", "5"))
MAX_LINES = int(os.getenv("PNKLN_GL_MAX_LINES", "300"))
WRITE_PATHS = os.getenv("PNKLN_GL_WRITE_PATHS", "src,lib,Sources").split(",")


def run_tests(cmd="pytest -q"):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode == 0, (p.stdout + "\n" + p.stderr)


def ask_vertex_for_patch(test_output: str):
    prompt = f"""You are pnkln repair agent.
Return a unified diff only (no prose). Max {MAX_LINES} lines.
Allowed paths: {", ".join(WRITE_PATHS)}.
Test Output:

{test_output}
"""
    model = v.TextGenerationModel.from_pretrained(MODEL_ID)
    resp = model.predict(prompt=prompt, temperature=0.2, max_output_tokens=2048)
    return resp.text or ""


def write_patch_to_file(patch: str, path="pnkln_out/patch.diff"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(patch)
    return path


def main():
    for _i in range(1, MAX_ITERS + 1):
        ok, out = run_tests()
        if ok:
            print("GREEN")
            return 0
        patch = ask_vertex_for_patch(out)
        lines = patch.count("\n")
        if lines > MAX_LINES or "diff" not in patch[:20].lower():
            print("SKIP: bad patch")
            return 2
        fp = write_patch_to_file(patch)
        print("PATCH_WRITTEN", fp)
    print("MAX_ITERS")
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
