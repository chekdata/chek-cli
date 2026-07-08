"""Setup for CHEK CLI."""

from pathlib import Path
from setuptools import find_namespace_packages, setup


ROOT = Path(__file__).parent
README = ROOT / "README.md"


def read_readme() -> str:
    try:
        return README.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


setup(
    name="chek-cli",
    version="0.5.0",
    author="CHEK frontend contributors",
    description="Agent-first CLI for CHEK product publication, review rooms, and backend capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/chekdata/chek-cli",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1,<9.0",
        "prompt-toolkit>=3.0,<4.0",
    ],
    extras_require={
        "browser": [
            "playwright>=1.40,<2.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "PyYAML>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chek=cli_anything.frontend_app.frontend_cli:main",
            "chek-cli=cli_anything.frontend_app.frontend_cli:main",
        ],
    },
    package_data={
        "cli_anything.frontend_app": ["skills/*.md", "generated/*.json"],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
