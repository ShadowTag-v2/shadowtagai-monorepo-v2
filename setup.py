# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
KERNEL Prompt Engineering Framework
Setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
  name="kernel-prompt-framework",
  version="1.0.0",
  description="KERNEL Prompt Engineering Framework - Validate and optimize AI prompts",
  long_description=long_description,
  long_description_content_type="text/markdown",
  author="PNKLN Core Stack",
  author_email="",
  url="https://github.com/ehanc69/aiyou-fastapi-services",
  packages=find_packages(where="src"),
  package_dir={"": "src"},
  python_requires=">=3.11",
  install_requires=[
    # No external dependencies - uses stdlib only
  ],
  extras_require={
    "dev": [
      "pytest>=7.0.0",
      "black>=23.0.0",
      "mypy>=1.0.0",
    ],
    "sdk": [
      "claude-agent-sdk>=0.1.6",
    ],
  },
  entry_points={
    "console_scripts": [
      "kernel=prompt_engineering.cli:main",
    ],
  },
  classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
  ],
  keywords="prompt-engineering ai llm kernel validation optimization",
)
