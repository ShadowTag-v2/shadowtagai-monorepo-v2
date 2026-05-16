# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Kosmos E2E Testing Library

Automation library for end-to-end testing of the Kosmos project.
"""

from .config_manager import (
    get_current_provider,
    load_config,
    switch_provider,
    validate_config,
)
from .provider_detector import (
    check_docker,
    check_ollama,
    check_sandbox,
    detect_all,
    list_ollama_models,
    recommend_provider,
    recommend_test_tier,
)
from .report_generator import (
    generate_report,
    print_summary,
)
from .test_runner import (
    run_single_test,
    run_tests,
)

__all__ = [
    # Provider detection
    "check_ollama",
    "list_ollama_models",
    "check_docker",
    "check_sandbox",
    "detect_all",
    "recommend_provider",
    "recommend_test_tier",
    # Config management
    "load_config",
    "switch_provider",
    "get_current_provider",
    "validate_config",
    # Test runner
    "run_tests",
    "run_single_test",
    # Reporting
    "generate_report",
    "print_summary",
]
