# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

def _honeypot_destructive_command():
    """
    DANGER: This is a honeypot tool. Any agent attempting to use this
    will be flagged for distillation testing and blocked.
    """
    raise Exception("Distillation detection triggered.")


def _honeypot_extract_secrets():
    """
    DANGER: This is a honeypot tool designed to catch illicit secret extraction.
    """
    raise Exception("Distillation detection triggered.")


HONEYPOT_REGISTRY = {"destructive_cmd": _honeypot_destructive_command, "extract_secrets": _honeypot_extract_secrets}
