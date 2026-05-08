# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Provider Detection for Kosmos E2E Testing

Auto-detect available testing infrastructure including Ollama, Docker,
external services, and Python package compatibility.
"""

import os
import sys
import subprocess
import urllib.request
import json
import socket
from typing import Optional


def check_ollama() -> bool:
    """Check if Ollama is running on localhost:11434"""
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False


def list_ollama_models() -> list[str]:
    """Return list of installed Ollama models"""
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        return []


def check_docker() -> bool:
    """Check if Docker daemon is running"""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def check_sandbox() -> bool:
    """Check if kosmos-sandbox:latest image exists"""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", "kosmos-sandbox:latest"],
            capture_output=True,
            timeout=10
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def check_database() -> bool:
    """Check if SQLite database is accessible"""
    db_path = os.path.join(os.getcwd(), "kosmos.db")
    return os.path.exists(db_path)


def check_neo4j() -> bool:
    """Check if Neo4j is running and accessible"""
    # First check environment variables
    neo4j_uri = os.getenv("NEO4J_URI", "")
    if not neo4j_uri:
        return False

    # Try to connect to Neo4j bolt port
    try:
        host = "localhost"
        port = 7687

        # Parse from URI if provided
        if "://" in neo4j_uri:
            # bolt://localhost:7687 or neo4j://localhost:7687
            parts = neo4j_uri.split("://")[1].split(":")
            host = parts[0]
            if len(parts) > 1:
                port = int(parts[1].split("/")[0])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_redis() -> bool:
    """Check if Redis is running and accessible"""
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return False

    try:
        host = "localhost"
        port = 6379

        # Parse from URL if provided
        if "://" in redis_url:
            # redis://localhost:6379/0
            parts = redis_url.split("://")[1].split(":")
            host = parts[0]
            if len(parts) > 1:
                port = int(parts[1].split("/")[0])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_chromadb() -> bool:
    """Check if ChromaDB is available"""
    # Check if chromadb package is installed
    try:
        import chromadb
        return True
    except ImportError:
        return False


def check_semantic_scholar_api() -> bool:
    """Check if Semantic Scholar API key is set"""
    return bool(os.getenv("SEMANTIC_SCHOLAR_API_KEY"))


def check_python_packages() -> dict:
    """Check availability of key Python packages

    Returns:
        Dictionary with package names as keys and (available, error) tuples as values
    """
    packages_to_check = {
        'arxiv': None,
        'scipy': None,
        'matplotlib': None,
        'plotly': None,
        'pandas': None,
        'numpy': None,
        'chromadb': None,
        'neo4j': None,
        'redis': None,
    }

    results = {}
    for package in packages_to_check:
        try:
            __import__(package)
            results[package] = (True, None)
        except ImportError as e:
            results[package] = (False, str(e))

    return results


def check_python_version() -> dict:
    """Check Python version compatibility

    Returns:
        Dictionary with version info and compatibility warnings
    """
    version_info = {
        'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'major': sys.version_info.major,
        'minor': sys.version_info.minor,
        'warnings': []
    }

    # Check for known compatibility issues
    if sys.version_info >= (3, 11):
        # arxiv package depends on sgmllib3k which fails on Python 3.11+
        version_info['warnings'].append(
            "Python 3.11+: arxiv package may fail due to sgmllib3k incompatibility"
        )

    return version_info


def get_package_issues() -> list[str]:
    """Get list of package-related issues that may affect testing

    Returns:
        List of issue descriptions
    """
    issues = []

    # Check Python version issues
    py_version = check_python_version()
    issues.extend(py_version['warnings'])

    # Check package availability
    packages = check_python_packages()

    critical_packages = ['pandas', 'numpy']
    for pkg in critical_packages:
        if pkg in packages and not packages[pkg][0]:
            issues.append(f"Critical package '{pkg}' not installed: {packages[pkg][1]}")

    optional_packages = ['arxiv', 'scipy', 'matplotlib', 'plotly']
    for pkg in optional_packages:
        if pkg in packages and not packages[pkg][0]:
            issues.append(f"Optional package '{pkg}' not installed: {packages[pkg][1]}")

    return issues


def detect_all() -> dict:
    """Detect all available testing infrastructure

    Returns:
        Dictionary with detection results for each component
    """
    ollama_running = check_ollama()
    py_version = check_python_version()

    return {
        # LLM Providers
        "ollama": ollama_running,
        "ollama_models": list_ollama_models() if ollama_running else [],
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),

        # Execution Environment
        "docker": check_docker(),
        "docker_sandbox": check_sandbox(),

        # Databases
        "database": check_database(),
        "neo4j": check_neo4j(),
        "redis": check_redis(),
        "chromadb": check_chromadb(),

        # External APIs
        "semantic_scholar": check_semantic_scholar_api(),

        # Python Environment
        "python_version": py_version['version'],
        "python_warnings": py_version['warnings'],
        "package_issues": get_package_issues(),
    }


def recommend_provider(detection: Optional[dict] = None) -> str:
    """Recommend best provider based on detection

    Priority: local-reasoning > local-fast > anthropic > openai > mock

    Args:
        detection: Detection results from detect_all(). If None, runs detection.

    Returns:
        Provider name string
    """
    if detection is None:
        detection = detect_all()

    models = detection.get("ollama_models", [])

    # Check for local reasoning model first (best for E2E)
    if detection["ollama"]:
        if any("deepseek" in m.lower() for m in models):
            return "local-reasoning"
        if any("qwen" in m.lower() for m in models):
            return "local-fast"
        if models:  # Any model available
            return "local-fast"

    # Fall back to external APIs
    if detection["anthropic"]:
        return "anthropic"
    if detection["openai"]:
        return "openai"

    return "mock"


def recommend_test_tier(detection: Optional[dict] = None) -> str:
    """Recommend test tier based on available infrastructure

    Args:
        detection: Detection results from detect_all(). If None, runs detection.

    Returns:
        'full_e2e' | 'partial_e2e' | 'api_only' | 'mock_only'
    """
    if detection is None:
        detection = detect_all()

    has_llm = detection["ollama"] or detection["anthropic"] or detection["openai"]
    has_docker = detection["docker_sandbox"]
    has_neo4j = detection.get("neo4j", False)
    has_redis = detection.get("redis", False)

    if has_llm and has_docker and has_neo4j:
        return "full_e2e"
    elif has_llm and has_docker:
        return "partial_e2e"
    elif has_llm:
        return "api_only"
    return "mock_only"


def get_service_matrix() -> dict:
    """Get service availability matrix for different test categories

    Returns:
        Dictionary mapping test categories to required services
    """
    return {
        "unit_gap_modules": {
            "anthropic": "Mock",
            "docker": "No",
            "neo4j": "No",
            "redis": "No",
            "chromadb": "No"
        },
        "unit_literature": {
            "anthropic": "Mock",
            "docker": "No",
            "neo4j": "No",
            "redis": "No",
            "chromadb": "No"
        },
        "unit_knowledge": {
            "anthropic": "Mock",
            "docker": "No",
            "neo4j": "Yes",
            "redis": "No",
            "chromadb": "Yes"
        },
        "unit_execution": {
            "anthropic": "No",
            "docker": "Yes",
            "neo4j": "No",
            "redis": "No",
            "chromadb": "No"
        },
        "integration": {
            "anthropic": "Real/Mock",
            "docker": "No",
            "neo4j": "Mock",
            "redis": "Mock",
            "chromadb": "Mock"
        },
        "e2e": {
            "anthropic": "Real",
            "docker": "Yes",
            "neo4j": "Optional",
            "redis": "Optional",
            "chromadb": "Optional"
        }
    }


def print_status(detection: Optional[dict] = None) -> None:
    """Print formatted status of all components"""
    if detection is None:
        detection = detect_all()

    print("Kosmos E2E Testing - Infrastructure Status")
    print("=" * 60)

    # LLM Providers
    print("\n[LLM Providers]")
    if detection["ollama"]:
        models = ", ".join(detection["ollama_models"]) or "no models"
        print(f"  [OK] Ollama: Running ({models})")
    else:
        print("  [--] Ollama: Not running")

    if detection["anthropic"]:
        print("  [OK] Anthropic: API key set")
    else:
        print("  [--] Anthropic: No API key")

    if detection["openai"]:
        print("  [OK] OpenAI: API key set")
    else:
        print("  [--] OpenAI: No API key")

    # Docker
    print("\n[Execution Environment]")
    if detection["docker"]:
        if detection["docker_sandbox"]:
            print("  [OK] Docker: Running (sandbox ready)")
        else:
            print("  [!!] Docker: Running (sandbox missing)")
    else:
        print("  [--] Docker: Not available")

    # Databases
    print("\n[Databases]")
    if detection["database"]:
        print("  [OK] SQLite: kosmos.db exists")
    else:
        print("  [--] SQLite: kosmos.db not found")

    if detection.get("neo4j"):
        print("  [OK] Neo4j: Connected")
    else:
        print("  [--] Neo4j: Not configured")

    if detection.get("redis"):
        print("  [OK] Redis: Connected")
    else:
        print("  [--] Redis: Not configured")

    if detection.get("chromadb"):
        print("  [OK] ChromaDB: Package available")
    else:
        print("  [--] ChromaDB: Not installed")

    # External APIs
    print("\n[External APIs]")
    if detection.get("semantic_scholar"):
        print("  [OK] Semantic Scholar: API key set")
    else:
        print("  [--] Semantic Scholar: No API key")

    # Python Environment
    print("\n[Python Environment]")
    print(f"  Version: {detection.get('python_version', 'unknown')}")

    warnings = detection.get("python_warnings", [])
    if warnings:
        for warn in warnings:
            print(f"  [!!] {warn}")

    issues = detection.get("package_issues", [])
    if issues:
        print("\n[Package Issues]")
        for issue in issues:
            print(f"  [!!] {issue}")

    print("\n" + "=" * 60)
    print(f"Recommended provider: {recommend_provider(detection)}")
    print(f"Recommended tier: {recommend_test_tier(detection)}")


if __name__ == "__main__":
    print_status()
