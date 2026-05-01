"""
Input Tokenizer — Escape Sequence Boundary Detection

Port of Claude Code's ink/termio/tokenize.ts.
Splits terminal input into tokens: text chunks and raw escape sequences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .ansi import C0, ESC_TYPE, is_esc_final
from .csi import is_csi_final, is_csi_intermediate, is_csi_param

TokenType = Literal["text", "sequence"]


@dataclass(frozen=True, slots=True)
class Token:
    type: TokenType
    value: str


State = Literal[
    "ground",
    "escape",
    "escapeIntermediate",
    "csi",
    "ss3",
    "osc",
    "dcs",
    "apc",
]


@dataclass
class _InternalState:
    state: State = "ground"
    buffer: str = ""


@dataclass
class _TokenizeResult:
    tokens: list[Token] = field(default_factory=list)
    state: _InternalState = field(default_factory=_InternalState)


class Tokenizer:
    """Streaming tokenizer for terminal input."""

    def __init__(self, *, x10_mouse: bool = False) -> None:
        self._state: State = "ground"
        self._buffer: str = ""
        self._x10_mouse = x10_mouse

    def feed(self, input_str: str) -> list[Token]:
        r = _tokenize(input_str, self._state, self._buffer, False, self._x10_mouse)
        self._state = r.state.state
        self._buffer = r.state.buffer
        return r.tokens

    def flush(self) -> list[Token]:
        r = _tokenize("", self._state, self._buffer, True, self._x10_mouse)
        self._state = r.state.state
        self._buffer = r.state.buffer
        return r.tokens

    def reset(self) -> None:
        self._state = "ground"
        self._buffer = ""

    def get_buffer(self) -> str:
        return self._buffer


def _tokenize(
    input_str: str,
    init_state: State,
    init_buf: str,
    flush: bool,
    x10_mouse: bool,
) -> _TokenizeResult:
    tokens: list[Token] = []
    result = _InternalState(state=init_state)
    data = init_buf + input_str
    i = 0
    text_start = 0
    seq_start = 0

    def flush_text() -> None:
        nonlocal text_start
        if i > text_start:
            t = data[text_start:i]
            if t:
                tokens.append(Token(type="text", value=t))
        text_start = i

    def emit_seq(seq: str) -> None:
        nonlocal text_start
        if seq:
            tokens.append(Token(type="sequence", value=seq))
        result.state = "ground"
        text_start = i

    while i < len(data):
        code = ord(data[i])

        if result.state == "ground":
            if code == C0.ESC:
                flush_text()
                seq_start = i
                result.state = "escape"
            i += 1

        elif result.state == "escape":
            if code == ESC_TYPE.CSI:
                result.state = "csi"
                i += 1
            elif code == ESC_TYPE.OSC:
                result.state = "osc"
                i += 1
            elif code == ESC_TYPE.DCS:
                result.state = "dcs"
                i += 1
            elif code == ESC_TYPE.APC:
                result.state = "apc"
                i += 1
            elif code == 0x4F:
                result.state = "ss3"
                i += 1
            elif is_csi_intermediate(code):
                result.state = "escapeIntermediate"
                i += 1
            elif is_esc_final(code):
                i += 1
                emit_seq(data[seq_start:i])
            elif code == C0.ESC:
                emit_seq(data[seq_start:i])
                seq_start = i
                result.state = "escape"
                i += 1
            else:
                result.state = "ground"
                text_start = seq_start

        elif result.state == "escapeIntermediate":
            if is_csi_intermediate(code):
                i += 1
            elif is_esc_final(code):
                i += 1
                emit_seq(data[seq_start:i])
            else:
                result.state = "ground"
                text_start = seq_start

        elif result.state == "csi":
            if (
                x10_mouse
                and code == 0x4D
                and i - seq_start == 2
                and (i + 1 >= len(data) or ord(data[i + 1]) >= 0x20)
                and (i + 2 >= len(data) or ord(data[i + 2]) >= 0x20)
                and (i + 3 >= len(data) or ord(data[i + 3]) >= 0x20)
            ):
                if i + 4 <= len(data):
                    i += 4
                    emit_seq(data[seq_start:i])
                else:
                    i = len(data)
            elif is_csi_final(code):
                i += 1
                emit_seq(data[seq_start:i])
            elif is_csi_param(code) or is_csi_intermediate(code):
                i += 1
            else:
                result.state = "ground"
                text_start = seq_start

        elif result.state == "ss3":
            if 0x40 <= code <= 0x7E:
                i += 1
                emit_seq(data[seq_start:i])
            else:
                result.state = "ground"
                text_start = seq_start

        elif result.state in ("osc", "dcs", "apc"):
            if code == C0.BEL:
                i += 1
                emit_seq(data[seq_start:i])
            elif code == C0.ESC and i + 1 < len(data) and ord(data[i + 1]) == ESC_TYPE.ST:
                i += 2
                emit_seq(data[seq_start:i])
            else:
                i += 1

    if result.state == "ground":
        flush_text()
    elif flush:
        rem = data[seq_start:]
        if rem:
            tokens.append(Token(type="sequence", value=rem))
        result.state = "ground"
    else:
        result.buffer = data[seq_start:]

    return _TokenizeResult(tokens=tokens, state=result)
