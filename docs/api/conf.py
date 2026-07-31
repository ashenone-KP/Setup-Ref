"""Sphinx configuration for the SupervisorMatch API documentation.

The documentation is generated automatically from the application's docstrings
(autodoc + Napoleon) and published on Read the Docs.
"""
import os
import sys

# Make the project importable for autodoc (repo root is two levels up).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

project = "SupervisorMatch"
author = "Patrik Katona"
copyright = "2026, Patrik Katona"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

exclude_patterns = ["_build"]

# Fall back to the default theme if the RTD theme is not installed locally.
try:
    import sphinx_rtd_theme  # noqa: F401
    html_theme = "sphinx_rtd_theme"
except ImportError:
    html_theme = "alabaster"

html_title = "SupervisorMatch API documentation"
