"""File Utilities
=============

Utilities for safe file handling and path manipulation.
"""

import os
import re
import unicodedata


def sanitize_filename(filename: str | None) -> str:
    """Sanitize a filename to prevent path traversal and ensure filesystem safety.

    - Normalizes unicode characters
    - Removes dangerous characters
    - Ensures no path separators
    - Prevents ".." traversal
    - Limits length
    """
    if not filename:
        return "unnamed_file"

    # Normalize unicode characters
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # Get the basename (removes directories)
    filename = os.path.basename(filename)

    # Replace dangerous characters with underscore
    # Allow: alphanumeric, dot, hyphen, underscore
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Ensure it's not empty after sanitization
    if not filename:
        return "unnamed_file"

    # Check for reserved names (Windows mostly, but good practice)
    # CON, PRN, AUX, NUL, COM1, LPT1, etc.
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        filename = f"_{filename}"

    return filename
