import unittest
from unittest.mock import MagicMock, patch

from shadowtag_v4.agents.repair_loop import SovereignRepairLoop


class TestRepairLoop(unittest.TestCase):
    @patch("shadowtag_v4.agents.repair_loop.genai")
    @patch("shadowtag_v4.agents.repair_loop.subprocess")
    def test_fix_cycle(self, mock_subprocess, mock_genai):
        # 1. Setup Mocks
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        # Mock Fixer Response
        mock_fix_response = MagicMock()
        mock_fix_response.text = "```python\nprint('Fixed')\n```"

        # Mock Reviewer Response (Approved)
        mock_review_response = MagicMock()
        mock_review_response.text = '{"approved": true, "reason": "Looks good"}'

        # Configure calls
        mock_client.models.generate_content.side_effect = [
            mock_fix_response,  # Fixer call
            mock_review_response,  # Reviewer call
        ]

        # 2. Execute
        loop = SovereignRepairLoop()
        result = loop.execute_loop("SyntaxError", "print('Error'", "test.py")

        # 3. Verify
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("PR Created", result["report"])

        # Verify GH CLI was called
        # The last call is likely checking out main, so we check if 'gh' was called in any step
        gh_called = False
        for call in mock_subprocess.run.call_args_list:
            args = call[0][0]
            if args[0] == "gh" and args[1] == "pr":
                gh_called = True
                break

        self.assertTrue(gh_called, "GitHub CLI (gh pr create) was not called")


if __name__ == "__main__":
    unittest.main()
