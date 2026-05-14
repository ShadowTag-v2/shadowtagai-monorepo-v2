# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from setuptools import setup, find_packages

setup(
    name="pnkln-file-search",
    version="0.1.0",
    description="Google File Search Integration for Pnkln Core Stack",
    author="Pnkln Core Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "google-cloud-aiplatform>=1.42.1",
        "google-cloud-storage>=2.14.0",
        "vertexai>=1.42.1",
        "aiohttp>=3.9.1",
        "prometheus-client>=0.19.0",
        "structlog>=23.3.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.21.1",
            "httpx>=0.26.0",
            "black>=23.12.1",
            "ruff>=0.1.9",
        ]
    },
    entry_points={
        "console_scripts": [
            "pnkln-file-search=pnkln_file_search.main:main",
        ],
    },
)
