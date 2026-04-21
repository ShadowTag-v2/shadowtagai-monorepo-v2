"""ShadowTag v2 Setup Script.

Installation:
    pip install -e .

Or with optional dependencies:
    pip install -e ".[full]"
    pip install -e ".[dev]"
"""

import os

from setuptools import find_packages, setup


# Read README for long description
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    return ""


setup(
    name="shadowtag-v2",
    version="1.0.0",
    author="ShadowTag Development Team",
    author_email="dev@shadowtag.ai",
    description="Production-grade video and audio watermarking system",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ehanc69/ShadowTag-v2-fastapi-services",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "opencv-python>=4.5.0",
        "PyWavelets>=1.1.1",
        "librosa>=0.9.0",
        "soundfile>=0.10.3",
        "numba>=0.53.0",
        "cryptography>=3.4.0",
        "reedsolo>=1.5.4",
    ],
    extras_require={
        "full": [
            "google-cloud-secret-manager>=2.0.0",
            "web3>=5.0.0",
            "scikit-image>=0.18.0",
            "ffmpeg-python>=0.2.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "gcp": [
            "google-cloud-secret-manager>=2.0.0",
        ],
        "blockchain": [
            "web3>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shadowtag=shadowtag_v2.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
