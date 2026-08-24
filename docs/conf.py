"""Sphinx configuration.

The prose is Markdown so it stays readable on GitHub; MyST renders it here
without a second source format. The API reference comes from the docstrings,
so nothing is written twice.

Build it with::

    poetry install --with docs
    poetry run sphinx-build -b html -W --keep-going docs docs/_build/html
"""

from __future__ import annotations

import sys
from datetime import date
from importlib.metadata import version as package_version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "rs-files-templates"
author = "Mariia Steeghs-Turchina"
copyright = f"{date.today().year}, Leiden University Medical Center"
release = package_version(project)
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
exclude_patterns = ["_build"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3
myst_fence_as_directive = ["mermaid"]

html_theme = "sphinx_book_theme"
html_title = f"{project} {release}"
html_static_path: list[str] = []
html_theme_options = {
    "repository_url": "https://github.com/LUMC-DCC/rs-files-templates",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "use_source_button": True,
    "home_page_in_toc": True,
    "show_toc_level": 2,
    "navigation_with_keys": False,
}

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_rtype = False
napoleon_use_ivar = True

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
