"""
agnt_termio — Terminal I/O escape sequence parser

Port of Claude Code's ink/termio module.
Provides streaming ANSI escape sequence parsing with semantic actions,
tokenization, and output generation utilities.

Submodules:
    ansi      — C0 control characters, ESC constants
    csi       — CSI sequences (cursor, erase, scroll, modes)
    dec       — DEC private mode sequences
    esc       — Simple ESC sequence parser
    sgr       — SGR (Select Graphic Rendition) parser
    osc       — OSC sequences (clipboard, hyperlinks, tab-status)
    tokenizer — Streaming escape sequence boundary detector
    parser    — Semantic action parser (main entry point)
    types     — All dataclass action types
"""

from .parser import Parser
from .tokenizer import Token, Tokenizer

__all__ = ["Parser", "Token", "Tokenizer"]
