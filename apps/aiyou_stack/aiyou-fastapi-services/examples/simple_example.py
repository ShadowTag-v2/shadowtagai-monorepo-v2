#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Simple example script demonstrating the Code Refactorer API.

Usage:
    python simple_example.py
"""

import json

import requests

SERVICE_URL = "http://localhost:8080"


def refactor_example():
    """Example: Refactor Python code."""
    print("=" * 60)
    print("Example 1: Refactoring Python Code")
    print("=" * 60)

    code = """
def f(x):
    r=[]
    for i in range(len(x)):
        if x[i]%2==0:
            r.append(x[i]*2)
    return r
"""

    payload = {"code": code, "language": "python", "refactor_type": "full"}

    response = requests.post(f"{SERVICE_URL}/api/v1/refactor/", json=payload)

    if response.status_code == 200:
        result = response.json()
        print("\nOriginal Code:")
        print(result["original_code"])
        print("\nRefactored Code:")
        print(result["refactored_code"])
        print("\nImprovements:")
        for imp in result["improvements"]:
            print(f"  - {imp}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def analyze_example():
    """Example: Analyze code quality."""
    print("\n" + "=" * 60)
    print("Example 2: Code Quality Analysis")
    print("=" * 60)

    code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

    payload = {"code": code, "language": "python"}

    response = requests.post(f"{SERVICE_URL}/api/v1/refactor/analyze", json=payload)

    if response.status_code == 200:
        result = response.json()
        print("\nCode Quality Score:", result.get("overall_quality_score", "N/A"))
        print("\nMetrics:")
        for metric, value in result["metrics"].items():
            print(f"  {metric}: {value}")
        print("\nSuggestions:")
        for suggestion in result["suggestions"]:
            print(f"  - {suggestion}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def health_check():
    """Check if the service is running."""
    print("\n" + "=" * 60)
    print("Health Check")
    print("=" * 60)

    try:
        response = requests.get(f"{SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("\nService is running!")
            print(json.dumps(response.json(), indent=2))
            return True
        print(f"\nService returned status: {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to service: {e}")
        print(f"\nMake sure the service is running at {SERVICE_URL}")
        return False


def main():
    """Run all examples."""
    print("\nCode Refactorer API - Simple Examples")
    print("=" * 60)

    if not health_check():
        print("\nPlease start the service first:")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8080")
        return

    refactor_example()
    analyze_example()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nFor more examples, see:")
    print(f"  - API docs: {SERVICE_URL}/docs")
    print("  - Jupyter notebook: examples/vertex_workbench_example.ipynb")


if __name__ == "__main__":
    main()
