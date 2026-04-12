#!/usr/bin/env python3
"""
Vulnerability Analysis Task for Gemini Code Assist
Analyzes all dependency files and identifies security issues.

Usage:
    python3 scripts/analyze-vulnerabilities.py

Requires: google-genai
"""

import os
from pathlib import Path

# Try to import Gemini (new SDK)
try:
    from google import genai
    from google.genai import types

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-genai not installed. Run: pip3 install google-genai")

PROJECT_ROOT = Path(__file__).parent.parent


def find_dependency_files() -> dict[str, list[Path]]:
    """Find all package.json and requirements.txt files."""
    files = {
        "npm": list(PROJECT_ROOT.glob("**/package.json")),
        "pip": list(PROJECT_ROOT.glob("**/requirements*.txt")),
        "pyproject": list(PROJECT_ROOT.glob("**/pyproject.toml")),
    }

    # Filter out node_modules and other excluded paths
    exclude = ["node_modules", ".venv", "venv", "__pycache__", ".git"]
    for key in files:
        files[key] = [f for f in files[key] if not any(ex in str(f) for ex in exclude)]

    return files


def read_file_contents(files: list[Path], max_size: int = 50000) -> str:
    """Read and concatenate file contents."""
    contents = []
    total_size = 0

    for f in files:
        try:
            content = f.read_text()
            if total_size + len(content) > max_size:
                contents.append(f"# {f.relative_to(PROJECT_ROOT)} [TRUNCATED]")
                break
            contents.append(f"# === {f.relative_to(PROJECT_ROOT)} ===\n{content}")
            total_size += len(content)
        except Exception as e:
            contents.append(f"# {f.relative_to(PROJECT_ROOT)} [ERROR: {e}]")

    return "\n\n".join(contents)


def analyze_with_gemini(dep_files: dict[str, list[Path]]) -> str:
    """Send dependency files to Gemini for analysis."""
    if not GEMINI_AVAILABLE:
        return "Gemini not available"

    # Configure Gemini (new SDK) - try ADC first (more reliable with Workspace), then API key
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "ag-shard-01")

    client = None

    # Try Vertex AI with ADC first (works with Workspace accounts)
    try:
        print(f"🔐 Using Vertex AI with project: {project}...")
        client = genai.Client(vertexai=True, project=project, location="us-central1")
    except Exception as e:
        print(f"⚠️ Vertex AI auth failed: {e}")

    # Fall back to API key if ADC fails
    if client is None and api_key:
        try:
            print("🔑 Trying API key authentication...")
            client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"⚠️ API key failed: {e}")

    if client is None:
        return "❌ Authentication failed. Run 'gcloud auth application-default login' or set GOOGLE_API_KEY"

    # Prepare content
    npm_content = read_file_contents(dep_files["npm"])
    pip_content = read_file_contents(dep_files["pip"])

    prompt = f"""You are a security analyst reviewing dependency files for a monorepo.

## Task
Analyze these dependency files and identify:
1. **Critical vulnerabilities** - packages with known CVEs
2. **Outdated packages** - significantly behind latest versions
3. **Version conflicts** - same package with different versions
4. **Unused/redundant** - packages that appear duplicated
5. **Recommended fixes** - specific version bumps or replacements

## NPM Dependencies (package.json files)
{npm_content[:30000]}

## Python Dependencies (requirements.txt files)
{pip_content[:30000]}

## Output Format
Provide a structured analysis with:
- Priority (CRITICAL/HIGH/MEDIUM/LOW)
- Package name
- Current version (if specified)
- Issue description
- Recommended action

Focus on actionable items that can be fixed via Dependabot or manual PR.
"""

    print("🤖 Sending to Gemini 2.0 Flash for analysis...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=8192,
        ),
    )
    return response.text


def main():
    print("🔍 Scanning for dependency files...")
    dep_files = find_dependency_files()

    print("\nFound:")
    print(f"  - {len(dep_files['npm'])} package.json files")
    print(f"  - {len(dep_files['pip'])} requirements.txt files")
    print(f"  - {len(dep_files['pyproject'])} pyproject.toml files")

    # List files
    print("\n📦 NPM packages:")
    for f in dep_files["npm"][:10]:
        print(f"  - {f.relative_to(PROJECT_ROOT)}")
    if len(dep_files["npm"]) > 10:
        print(f"  ... and {len(dep_files['npm']) - 10} more")

    print("\n🐍 Python packages:")
    for f in dep_files["pip"][:10]:
        print(f"  - {f.relative_to(PROJECT_ROOT)}")
    if len(dep_files["pip"]) > 10:
        print(f"  ... and {len(dep_files['pip']) - 10} more")

    # Analyze with Gemini if available (supports API key or ADC)
    gemini_result = None
    if GEMINI_AVAILABLE:
        print("\n" + "=" * 60)
        try:
            gemini_result = analyze_with_gemini(dep_files)
            print("\n📊 Gemini Analysis:\n")
            print(gemini_result)
        except Exception as e:
            print(f"\n⚠️ Gemini analysis failed: {e}")
            print("\n💡 To fix authentication:")
            print("  Option A: API Key")
            print("    1. Get key from: https://aistudio.google.com/apikey")
            print("    2. export GOOGLE_API_KEY=your_api_key")
            print("  Option B: Google Cloud ADC")
            print("    1. gcloud auth application-default login")
            print("    2. export GOOGLE_CLOUD_PROJECT=your-project-id")
    else:
        print("\n⚠️ To enable Gemini analysis:")
        print("  pip3 install google-genai")

    # Save results
    output_file = PROJECT_ROOT / "reports" / "vulnerability-analysis.md"
    output_file.parent.mkdir(exist_ok=True)

    report = f"""# Vulnerability Analysis Report

Generated: {__import__("datetime").datetime.now().isoformat()}

## Dependency Files Found

- **NPM**: {len(dep_files["npm"])} files
- **Python**: {len(dep_files["pip"])} files
- **PyProject**: {len(dep_files["pyproject"])} files

## Files

### NPM (package.json)
{chr(10).join(f"- `{f.relative_to(PROJECT_ROOT)}`" for f in dep_files["npm"])}

### Python (requirements.txt)
{chr(10).join(f"- `{f.relative_to(PROJECT_ROOT)}`" for f in dep_files["pip"])}

## Next Steps

1. Run `npm audit` in directories with package.json
2. Run `pip-audit -r requirements.txt` for Python dependencies
3. Enable Dependabot auto-merge for patch/minor updates
4. Review Gemini analysis for prioritized fixes
"""

    output_file.write_text(report)
    print(f"\n✅ Report saved to: {output_file.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
