# Configuration file for the Sphinx documentation builder.

import os
import sys
from pathlib import Path

# Add source directory to path
sys.path.insert(0, os.path.abspath("../../src"))

# Project information
project = "YAPPLA"
copyright = "2024, Daniele Calisi"
author = "Daniele Calisi"
release = "0.0.3"

# The full version, including alpha/beta/rc tags
version = "0.0.3"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Master doc
master_doc = "index"

# List of patterns, relative to source directory, that should be ignored when building
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Theme configuration
# Using default Sphinx theme (alabaster)
# To use RTD theme: pip install sphinx_rtd_theme
# and uncomment the line below:
# html_theme = "sphinx_rtd_theme"
html_theme = "alabaster"

# Napoleon configuration for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_keyword = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# HTML output options
html_static_path = ["_static"]
html_logo = None
html_favicon = None

# LaTeX output options
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "11pt",
}

latex_documents = [
    (
        "index",
        "yappla.tex",
        "YAPPLA Documentation",
        "Daniele Calisi",
        "manual",
    ),
]
