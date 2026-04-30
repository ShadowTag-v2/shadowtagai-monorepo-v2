#!/usr/bin/env python3
"""Test script to validate Mobile Optimizer setup"""

import json
import sys
from pathlib import Path


def test_file_exists(path: Path, description: str) -> bool:
    """Test if a file exists"""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    print(f"✗ {description}: {path} NOT FOUND")
    return False


def test_json_valid(path: Path, description: str) -> bool:
    """Test if JSON file is valid"""
    if not path.exists():
        print(f"✗ {description}: {path} NOT FOUND")
        return False

    try:
        with open(path) as f:
            json.load(f)
        print(f"✓ {description}: Valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ {description}: Invalid JSON - {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Mobile Optimizer - Setup Validation")
    print("=" * 50)
    print()

    base_dir = Path(__file__).parent
    tests_passed = 0
    tests_total = 0

    # Test Python files
    print("📝 Python Files:")
    tests = [
        (base_dir / "main.py", "Main FastAPI app"),
        (base_dir / "generate_icons.py", "Icon generator"),
        (base_dir / "requirements.txt", "Requirements file"),
    ]
    for path, desc in tests:
        tests_total += 1
        if test_file_exists(path, desc):
            tests_passed += 1
    print()

    # Test static files
    print("🎨 Static Files:")
    tests = [
        (base_dir / "static/manifest.json", "PWA manifest"),
        (base_dir / "static/css/mobile-styles.css", "Mobile styles"),
        (base_dir / "static/js/app.js", "Main app JS"),
        (base_dir / "static/js/sw.js", "Service worker"),
        (base_dir / "static/js/touch-gestures.js", "Touch gestures"),
        (base_dir / "static/js/mobile-performance.js", "Performance utilities"),
    ]
    for path, desc in tests:
        tests_total += 1
        if test_file_exists(path, desc):
            tests_passed += 1
    print()

    # Test templates
    print("📄 Templates:")
    tests = [
        (base_dir / "templates/index.html", "Main template"),
        (base_dir / "templates/offline.html", "Offline template"),
    ]
    for path, desc in tests:
        tests_total += 1
        if test_file_exists(path, desc):
            tests_passed += 1
    print()

    # Test icons
    print("🖼️  PWA Icons:")
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    for size in icon_sizes:
        path = base_dir / f"static/icons/icon-{size}x{size}.png"
        tests_total += 1
        if test_file_exists(path, f"Icon {size}x{size}"):
            tests_passed += 1
    print()

    # Test Docker files
    print("🐳 Docker Files:")
    tests = [
        (base_dir / "Dockerfile", "Dockerfile"),
        (base_dir / "docker-compose.yml", "Docker Compose"),
        (base_dir / ".dockerignore", "Docker ignore"),
    ]
    for path, desc in tests:
        tests_total += 1
        if test_file_exists(path, desc):
            tests_passed += 1
    print()

    # Test configuration files
    print("⚙️  Configuration:")
    tests = [
        (base_dir / ".env.example", "Environment example"),
        (base_dir / ".gitignore", "Git ignore"),
    ]
    for path, desc in tests:
        tests_total += 1
        if test_file_exists(path, desc):
            tests_passed += 1
    print()

    # Test JSON validity
    print("🔍 JSON Validation:")
    tests_total += 1
    if test_json_valid(base_dir / "static/manifest.json", "PWA Manifest"):
        tests_passed += 1
    print()

    # Test directory structure
    print("📁 Directory Structure:")
    dirs = [
        (base_dir / "static", "Static directory"),
        (base_dir / "static/css", "CSS directory"),
        (base_dir / "static/js", "JavaScript directory"),
        (base_dir / "static/icons", "Icons directory"),
        (base_dir / "templates", "Templates directory"),
    ]
    for path, desc in dirs:
        tests_total += 1
        if path.is_dir():
            print(f"✓ {desc}: {path}")
            tests_passed += 1
        else:
            print(f"✗ {desc}: {path} NOT FOUND")
    print()

    # Summary
    print("=" * 50)
    print(f"📊 Results: {tests_passed}/{tests_total} tests passed")
    print()

    if tests_passed == tests_total:
        print("🎉 All tests passed! Your Mobile Optimizer is ready to use.")
        print()
        print("To start the application:")
        print("  ./run.sh")
        print("  OR")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return 0
    print("⚠️  Some tests failed. Please check the errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
