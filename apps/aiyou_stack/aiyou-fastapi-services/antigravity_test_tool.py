#!/usr/bin/env python3
import unittest
from unittest.mock import patch

import antigravity_service


class TestAntigravityLogic(unittest.TestCase):
    def test_tool_definitions(self):
        self.assertIn("function_declarations", antigravity_service.TOOL_DEFINITIONS)
        funcs = [f["name"] for f in antigravity_service.TOOL_DEFINITIONS["function_declarations"]]
        self.assertIn("code_search_tool", funcs)
        self.assertIn("list_files_tool", funcs)

    def test_pick_model(self):
        self.assertEqual(antigravity_service.pick_model("FREE"), "models/gemini-1.5-flash-8b-exp")
        self.assertEqual(antigravity_service.pick_model("FLASH"), "models/gemini-2.0-flash-exp")
        self.assertEqual(antigravity_service.pick_model("PRO"), "models/gemini-2.0-pro-exp")

    @patch("subprocess.check_output")
    def test_code_search_tool_execution(self, mock_subprocess):
        mock_subprocess.return_value = b"file.py:10:match found"
        result = antigravity_service.code_search_tool("query")
        self.assertEqual(result, {"result": "file.py:10:match found"})

    @patch("antigravity_service.call_gemini_turn")
    def test_agent_loop_simple(self, mock_gemini):
        # Mock a simple response with no tool calls
        mock_gemini.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Hello world"}]}}],
        }

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test"}):
            answer = antigravity_service.run_agent_loop("model", "hi")
            self.assertEqual(answer, "Hello world")

    @patch("antigravity_service.call_gemini_turn")
    def test_agent_loop_with_tool(self, mock_gemini):
        # Mock turn 1: Call tool
        resp1 = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"functionCall": {"name": "code_search_tool", "args": {"query": "foo"}}},
                        ],
                    },
                },
            ],
        }
        # Mock turn 2: Final answer
        resp2 = {"candidates": [{"content": {"parts": [{"text": "I found foo."}]}}]}
        mock_gemini.side_effect = [resp1, resp2]

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test"}):
            with patch("antigravity_service.code_search_tool") as mock_tool:
                mock_tool.return_value = {"result": "found it"}
                answer = antigravity_service.run_agent_loop("model", "search for foo")
                self.assertEqual(answer, "I found foo.")
                mock_tool.assert_called_with(query="foo")


if __name__ == "__main__":
    unittest.main()
