"""
CSI (Control Sequence Introducer) Types

Port of Claude Code's ink/termio/csi.ts.
"""

from __future__ import annotations

from .ansi import ESC, ESC_TYPE, SEP

CSI_PREFIX = ESC + chr(ESC_TYPE.CSI)


class CSI_RANGE:
    PARAM_START = 0x30
    PARAM_END = 0x3F
    INTERMEDIATE_START = 0x20
    INTERMEDIATE_END = 0x2F
    FINAL_START = 0x40
    FINAL_END = 0x7E


def is_csi_param(byte: int) -> bool:
    return CSI_RANGE.PARAM_START <= byte <= CSI_RANGE.PARAM_END


def is_csi_intermediate(byte: int) -> bool:
    return CSI_RANGE.INTERMEDIATE_START <= byte <= CSI_RANGE.INTERMEDIATE_END


def is_csi_final(byte: int) -> bool:
    return CSI_RANGE.FINAL_START <= byte <= CSI_RANGE.FINAL_END


def csi(*args: str | int) -> str:
    """Generate a CSI sequence: ESC [ p1;p2;...;pN final"""
    if len(args) == 0:
        return CSI_PREFIX
    if len(args) == 1:
        return f"{CSI_PREFIX}{args[0]}"
    params = args[:-1]
    final = args[-1]
    return f"{CSI_PREFIX}{SEP.join(str(p) for p in params)}{final}"


class CSI:
    CUU = 0x41
    CUD = 0x42
    CUF = 0x43
    CUB = 0x44
    CNL = 0x45
    CPL = 0x46
    CHA = 0x47
    CUP = 0x48
    CHT = 0x49
    VPA = 0x64
    HVP = 0x66
    ED = 0x4A
    EL = 0x4B
    ECH = 0x58
    IL = 0x4C
    DL = 0x4D
    ICH = 0x40
    DCH = 0x50
    SU = 0x53
    SD = 0x54
    SM = 0x68
    RM = 0x6C
    SGR = 0x6D
    DSR = 0x6E
    DECSCUSR = 0x71
    DECSTBM = 0x72
    SCOSC = 0x73
    SCORC = 0x75
    CBT = 0x5A


ERASE_DISPLAY = ("toEnd", "toStart", "all", "scrollback")
ERASE_LINE_REGION = ("toEnd", "toStart", "all")
CURSOR_STYLES = (
    {"style": "block", "blinking": True},
    {"style": "block", "blinking": True},
    {"style": "block", "blinking": False},
    {"style": "underline", "blinking": True},
    {"style": "underline", "blinking": False},
    {"style": "bar", "blinking": True},
    {"style": "bar", "blinking": False},
)


def cursor_up(n: int = 1) -> str:
    return "" if n == 0 else csi(n, "A")


def cursor_down(n: int = 1) -> str:
    return "" if n == 0 else csi(n, "B")


def cursor_forward(n: int = 1) -> str:
    return "" if n == 0 else csi(n, "C")


def cursor_back(n: int = 1) -> str:
    return "" if n == 0 else csi(n, "D")


def cursor_to(col: int) -> str:
    return csi(col, "G")


CURSOR_LEFT = csi("G")


def cursor_position(row: int, col: int) -> str:
    return csi(row, col, "H")


CURSOR_HOME = csi("H")


def cursor_move(x: int, y: int) -> str:
    result = ""
    if x < 0:
        result += cursor_back(-x)
    elif x > 0:
        result += cursor_forward(x)
    if y < 0:
        result += cursor_up(-y)
    elif y > 0:
        result += cursor_down(y)
    return result


CURSOR_SAVE = csi("s")
CURSOR_RESTORE = csi("u")


def erase_to_end_of_line() -> str:
    return csi("K")


def erase_line() -> str:
    return csi(2, "K")


ERASE_LINE = csi(2, "K")


def erase_screen() -> str:
    return csi(2, "J")


ERASE_SCREEN = csi(2, "J")
ERASE_SCROLLBACK = csi(3, "J")


def erase_lines(n: int) -> str:
    if n <= 0:
        return ""
    result = ""
    for i in range(n):
        result += ERASE_LINE
        if i < n - 1:
            result += cursor_up(1)
    result += CURSOR_LEFT
    return result


def scroll_up(n: int = 1) -> str:
    return "" if n == 0 else csi(n, "S")


def scroll_down(n: int = 1) -> str:
    return "" if n == 0 else csi(n, "T")


def set_scroll_region(top: int, bottom: int) -> str:
    return csi(top, bottom, "r")


RESET_SCROLL_REGION = csi("r")
PASTE_START = csi("200~")
PASTE_END = csi("201~")
FOCUS_IN = csi("I")
FOCUS_OUT = csi("O")

# Kitty keyboard protocol
ENABLE_KITTY_KEYBOARD = csi(">1u")
DISABLE_KITTY_KEYBOARD = csi("<u")
ENABLE_MODIFY_OTHER_KEYS = csi(">4;2m")
DISABLE_MODIFY_OTHER_KEYS = csi(">4m")
