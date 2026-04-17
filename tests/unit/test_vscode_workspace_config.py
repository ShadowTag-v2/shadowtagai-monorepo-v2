from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_jsonc(path: Path) -> dict:
    lines: list[str] = []
    for line in path.read_text().splitlines():
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        lines.append(line)
    return json.loads("\n".join(lines))


class WorkspaceConfigShapeTest(unittest.TestCase):
    def test_workspace_settings_file_has_settings_shape(self) -> None:
        settings = _load_jsonc(REPO_ROOT / ".vscode" / "settings.json")

        self.assertNotIn("configurations", settings)
        self.assertNotIn("version", settings)
        self.assertIn("editor.formatOnSave", settings)
        self.assertIn("python.defaultInterpreterPath", settings)

    def test_workspace_launch_file_has_launch_shape_if_present(self) -> None:
        launch_path = REPO_ROOT / ".vscode" / "launch.json"
        if not launch_path.exists():
            self.skipTest("workspace launch.json is optional and not repo-tracked")

        launch = _load_jsonc(launch_path)

        self.assertEqual("0.2.0", launch["version"])
        self.assertIsInstance(launch["configurations"], list)
        self.assertTrue(launch["configurations"])
