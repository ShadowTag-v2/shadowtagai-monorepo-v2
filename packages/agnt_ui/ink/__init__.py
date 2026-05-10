"""agnt_ui.ink — Safe Harbor compatibility shim.

The upstream React/Ink terminal UI is replaced by ``agnt_ui.renderer``
using Python ``rich``. This shim re-exports the renderer so any code
that imported from ``agnt_ui.ink`` continues to work.
"""

from agnt_ui.renderer import TerminalRenderer
from agnt_ui.spinner import AgntSpinner
from agnt_ui.status_bar import StatusBar

__all__ = ["AgntSpinner", "StatusBar", "TerminalRenderer"]
