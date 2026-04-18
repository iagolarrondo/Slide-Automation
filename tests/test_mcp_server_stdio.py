"""Smoke tests for the optional MCP stdio server module."""

from __future__ import annotations

import sys
import unittest


class TestMcpServerStdioModule(unittest.TestCase):
    def test_server_stdio_imports_without_mcp_sdk(self) -> None:
        from slide_automation.mcp import server_stdio

        self.assertTrue(callable(server_stdio.main))
        self.assertTrue(callable(server_stdio._build_app))

    @unittest.skipIf(sys.version_info < (3, 10), "MCP SDK requires Python >=3.10")
    def test_build_app_when_mcp_installed(self) -> None:
        try:
            import mcp.server.fastmcp  # noqa: F401
        except ImportError:
            self.skipTest("mcp extra not installed")
        from slide_automation.mcp.server_stdio import _build_app

        app = _build_app()
        self.assertEqual(app.name, "slide-automation")


if __name__ == "__main__":
    unittest.main()
