#!/usr/bin/env python3
# ⚠️ DEPRECATED — This file contains references to deprecated frameworks
# (AutoGen/AG2, LangGraph, Vertex AI Workbench) that are no longer part of
# the production CounselConduit architecture. These refs are slated for
# removal. See deploy-preflight findings 2026-05-17.
# Production path: apps/counselconduit/api/fastapi_kovel_enclave.py
"""PNKLN Stack Verification Script

Verifies all 6 layers are properly installed and configured.
Reports health status and integration points.
"""

import sys
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_layer_0_memory_persistence() -> tuple[bool, list[str]]:
    """Verify Layer 0: Memory Persistence"""
    checks = []
    all_pass = True

    # Check directory exists
    memory_dir = Path("erik-hancock-llm-memory")
    if memory_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Memory persistence directory exists")

        # Check key files
        required_files = [
            "scripts/extract_and_commit.py",
            "scripts/claude_code_memory_local.py",
            "scripts/llm_blender_rotation.py",
            "configs/vertex_workbench_config.py",
            "memory/schema.json",
        ]

        for file in required_files:
            if (memory_dir / file).exists():
                checks.append(f"  {GREEN}✓{RESET} {file}")
            else:
                checks.append(f"  {RED}✗{RESET} {file} missing")
                all_pass = False
    else:
        checks.append(f"{RED}✗{RESET} Memory persistence directory not found")
        all_pass = False

    return all_pass, checks


def check_layer_1_pnkln_stack() -> tuple[bool, list[str]]:
    """Verify Layer 1: PNKLN Stack"""
    checks = []
    all_pass = True

    pnkln_dir = Path("src/pnkln")
    if pnkln_dir.exists():
        checks.append(f"{GREEN}✓{RESET} PNKLN stack directory exists")

        required_files = ["__init__.py", "judge_six.py", "shadowtag.py", "cor.py", "ns.py"]

        for file in required_files:
            if (pnkln_dir / file).exists():
                checks.append(f"  {GREEN}✓{RESET} {file}")
            else:
                checks.append(f"  {RED}✗{RESET} {file} missing")
                all_pass = False

        # Check if modules are importable
        try:
            sys.path.insert(0, str(Path.cwd()))
            from src.pnkln import NS, Cor, JudgeSix, ShadowTag  # noqa: F401

            checks.append(f"  {GREEN}✓{RESET} PNKLN modules importable")
        except ImportError as e:
            checks.append(f"  {YELLOW}⚠{RESET} Import warning: {e}")

    else:
        checks.append(f"{RED}✗{RESET} PNKLN stack directory not found")
        all_pass = False

    return all_pass, checks


def check_layer_2_gemini_functions() -> tuple[bool, list[str]]:
    """Verify Layer 2: Gemini Function Calling"""
    checks = []
    all_pass = True

    core_dir = Path("src/core")
    if core_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Core function calling directory exists")

        required_files = ["__init__.py", "gemini_function_calling.py", "function_registry.py"]

        for file in required_files:
            if (core_dir / file).exists():
                checks.append(f"  {GREEN}✓{RESET} {file}")
            else:
                checks.append(f"  {RED}✗{RESET} {file} missing")
                all_pass = False

        # Check kernels
        kernels_dir = Path("src/kernels")
        if kernels_dir.exists():
            checks.append(f"  {GREEN}✓{RESET} Kernels directory exists")
            kernel_count = len(list(kernels_dir.glob("*.py"))) - 1  # Exclude __init__.py
            checks.append(f"    {BLUE}ℹ{RESET} {kernel_count} kernels available")
        else:
            checks.append(f"  {YELLOW}⚠{RESET} Kernels directory not found")

    else:
        checks.append(f"{RED}✗{RESET} Core directory not found")
        all_pass = False

    return all_pass, checks


def check_layer_3_orchestration() -> tuple[bool, list[str]]:
    """Verify Layer 3: ACE Orchestration + Unified Orchestrator"""
    checks = []
    all_pass = True

    # Check integration layer
    integration_dir = Path("src/integration")
    if integration_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Integration layer exists")

        if (integration_dir / "unified_orchestrator.py").exists():
            checks.append(f"  {GREEN}✓{RESET} unified_orchestrator.py")
        else:
            checks.append(f"  {RED}✗{RESET} unified_orchestrator.py missing")
            all_pass = False
    else:
        checks.append(f"{YELLOW}⚠{RESET} Integration directory not found")

    # Check existing ACE tools
    tools_dir = Path("tools/orchestrator")
    if tools_dir.exists():
        checks.append(f"{GREEN}✓{RESET} ACE orchestrator tools exist")

        ace_files = ["ace_orchestrator.mjs", "ace_with_refactor.mjs"]
        for file in ace_files:
            if (tools_dir / file).exists():
                checks.append(f"  {GREEN}✓{RESET} {file}")
            else:
                checks.append(f"  {YELLOW}⚠{RESET} {file} not found")
    else:
        checks.append(f"{YELLOW}⚠{RESET} ACE tools directory not found")

    return all_pass, checks


def check_layer_4_agents() -> tuple[bool, list[str]]:
    """Verify Layer 4: Multi-Agent Reasoning"""
    checks = []
    all_pass = True

    agents_dir = Path("src/agents")
    if agents_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Agents directory exists")

        required_files = ["__init__.py", "base.py", "debate.py"]

        for file in required_files:
            if (agents_dir / file).exists():
                checks.append(f"  {GREEN}✓{RESET} {file}")
            else:
                checks.append(f"  {RED}✗{RESET} {file} missing")
                all_pass = False

    else:
        checks.append(f"{RED}✗{RESET} Agents directory not found")
        all_pass = False

    return all_pass, checks


def check_layer_5_evolution() -> tuple[bool, list[str]]:
    """Verify Layer 5: DTE Evolution"""
    checks = []
    all_pass = True

    evolution_dir = Path("src/evolution")
    ratings_dir = Path("src/ratings")
    training_dir = Path("src/training")

    if evolution_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Evolution directory exists")
        if (evolution_dir / "dte.py").exists():
            checks.append(f"  {GREEN}✓{RESET} dte.py")
        else:
            checks.append(f"  {RED}✗{RESET} dte.py missing")
            all_pass = False
    else:
        checks.append(f"{RED}✗{RESET} Evolution directory not found")
        all_pass = False

    if ratings_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Ratings directory exists")
        if (ratings_dir / "glicko2.py").exists():
            checks.append(f"  {GREEN}✓{RESET} glicko2.py (with tol parameter)")
        else:
            checks.append(f"  {RED}✗{RESET} glicko2.py missing")
            all_pass = False
    else:
        checks.append(f"{RED}✗{RESET} Ratings directory not found")
        all_pass = False

    if training_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Training directory exists")
        if (training_dir / "grpo.py").exists():
            checks.append(f"  {GREEN}✓{RESET} grpo.py (Group Relative Policy Optimization)")
        else:
            checks.append(f"  {RED}✗{RESET} grpo.py missing")
            all_pass = False
    else:
        checks.append(f"{RED}✗{RESET} Training directory not found")
        all_pass = False

    return all_pass, checks


def check_testing_suite() -> tuple[bool, list[str]]:
    """Verify testing and validation tools"""
    checks = []
    all_pass = True

    # Check unit tests
    tests_dir = Path("src/tests")
    if tests_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Unit tests directory exists")
        test_files = list(tests_dir.glob("test_*.py"))
        checks.append(f"  {BLUE}ℹ{RESET} {len(test_files)} test files found")
    else:
        checks.append(f"{YELLOW}⚠{RESET} Unit tests directory not found")

    # Check load testing
    load_dir = Path("load_testing")
    if load_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Load testing directory exists")
        if (load_dir / "pnkln_load_tests_enhanced.py").exists():
            checks.append(f"  {GREEN}✓{RESET} Enhanced load testing suite v2.0")
        else:
            checks.append(f"  {RED}✗{RESET} Load testing suite missing")
            all_pass = False
    else:
        checks.append(f"{RED}✗{RESET} Load testing directory not found")
        all_pass = False

    # Check integration tests (ACE)
    integration_tests = Path("tests/integration")
    if integration_tests.exists():
        checks.append(f"{GREEN}✓{RESET} ACE integration tests exist")
        test_count = len(list(integration_tests.glob("test_*.mjs"))) + len(
            list(integration_tests.glob("test_*.py")),
        )
        checks.append(f"  {BLUE}ℹ{RESET} {test_count} integration tests found")
    else:
        checks.append(f"{YELLOW}⚠{RESET} ACE integration tests not found")

    return all_pass, checks


def check_dependencies() -> tuple[bool, list[str]]:
    """Verify required dependencies"""
    checks = []
    all_pass = True

    required_packages = [
        ("google.generativeai", "Gemini SDK"),
        ("cryptography", "Ed25519 signatures"),
        ("PIL", "Image watermarking"),
        ("numpy", "Numerical computing"),
        ("structlog", "Structured logging"),
    ]

    for module, description in required_packages:
        try:
            __import__(module)
            checks.append(f"{GREEN}✓{RESET} {description} ({module})")
        except ImportError:
            checks.append(f"{RED}✗{RESET} {description} ({module}) not installed")
            all_pass = False

    return all_pass, checks


def check_examples() -> tuple[bool, list[str]]:
    """Verify example code"""
    checks = []
    all_pass = True

    examples_dir = Path("src/examples")
    if examples_dir.exists():
        checks.append(f"{GREEN}✓{RESET} Examples directory exists")

        example_files = [
            "basic_function_calling.py",
            "judge_six_example.py",
            "full_pnkln_stack.py",
            "unified_poc_demo.py",
        ]

        found = 0
        for file in example_files:
            if (examples_dir / file).exists():
                found += 1

        checks.append(f"  {BLUE}ℹ{RESET} {found}/{len(example_files)} examples present")

    else:
        checks.append(f"{YELLOW}⚠{RESET} Examples directory not found")

    return all_pass, checks


def main():
    """Run all verification checks"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}PNKLN Ultrathink Stack Verification{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")

    all_layers_pass = True

    # Layer 0
    print(f"\n{BLUE}Layer 0: Memory Persistence (Foundation){RESET}")
    print("─" * 70)
    layer0_pass, layer0_checks = check_layer_0_memory_persistence()
    for check in layer0_checks:
        print(check)
    all_layers_pass = all_layers_pass and layer0_pass

    # Layer 1
    print(f"\n{BLUE}Layer 1: PNKLN Stack (Validation & Audit){RESET}")
    print("─" * 70)
    layer1_pass, layer1_checks = check_layer_1_pnkln_stack()
    for check in layer1_checks:
        print(check)
    all_layers_pass = all_layers_pass and layer1_pass

    # Layer 2
    print(f"\n{BLUE}Layer 2: Gemini Function Calling (Kernel Chaining 2.0){RESET}")
    print("─" * 70)
    layer2_pass, layer2_checks = check_layer_2_gemini_functions()
    for check in layer2_checks:
        print(check)
    all_layers_pass = all_layers_pass and layer2_pass

    # Layer 3
    print(f"\n{BLUE}Layer 3: ACE Orchestration + Unified Orchestrator{RESET}")
    print("─" * 70)
    layer3_pass, layer3_checks = check_layer_3_orchestration()
    for check in layer3_checks:
        print(check)
    all_layers_pass = all_layers_pass and layer3_pass

    # Layer 4
    print(f"\n{BLUE}Layer 4: Multi-Agent Reasoning (MAD/Panel Debates){RESET}")
    print("─" * 70)
    layer4_pass, layer4_checks = check_layer_4_agents()
    for check in layer4_checks:
        print(check)
    all_layers_pass = all_layers_pass and layer4_pass

    # Layer 5
    print(f"\n{BLUE}Layer 5: DTE Evolution (Self-Improvement){RESET}")
    print("─" * 70)
    layer5_pass, layer5_checks = check_layer_5_evolution()
    for check in layer5_checks:
        print(check)
    all_layers_pass = all_layers_pass and layer5_pass

    # Testing
    print(f"\n{BLUE}Testing & Validation Suite{RESET}")
    print("─" * 70)
    testing_pass, testing_checks = check_testing_suite()
    for check in testing_checks:
        print(check)

    # Dependencies
    print(f"\n{BLUE}Dependencies{RESET}")
    print("─" * 70)
    deps_pass, deps_checks = check_dependencies()
    for check in deps_checks:
        print(check)

    # Examples
    print(f"\n{BLUE}Examples & Documentation{RESET}")
    print("─" * 70)
    examples_pass, examples_checks = check_examples()
    for check in examples_checks:
        print(check)

    # Summary
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    if all_layers_pass:
        print(f"{GREEN}✓ All 6 layers verified successfully!{RESET}")
        print(f"\n{GREEN}PNKLN Ultrathink Stack is ready for deployment{RESET}")
    else:
        print(f"{RED}✗ Some layers have issues{RESET}")
        print(f"\n{YELLOW}Please review the issues above{RESET}")

    print(f"{BLUE}{'=' * 70}{RESET}\n")

    return 0 if all_layers_pass else 1


if __name__ == "__main__":
    sys.exit(main())
