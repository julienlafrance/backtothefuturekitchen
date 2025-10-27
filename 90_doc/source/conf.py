# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the path to the source code
sys.path.insert(0, os.path.abspath('../../10_preprod/src'))

# -- Project information -----------------------------------------------------
project = 'Mangetamain Analytics'
copyright = '2025, Mangetamain Team'
author = 'Mangetamain Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Automatic documentation from docstrings
    'sphinx.ext.napoleon',     # Support for Google/NumPy docstrings
    'sphinx.ext.viewcode',     # Add links to source code
    'sphinx.ext.intersphinx',  # Link to other documentation
    'myst_parser',             # Markdown support
    'sphinx_rtd_theme',        # Read the Docs theme
]

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Napoleon settings (Google style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Mock imports for dependencies not installed in docs environment
autodoc_mock_imports = [
    'streamlit',
    'plotly',
    'pandas',
    'polars',
    'numpy',
    'duckdb',
    'boto3',
    'loguru',
]

# Templates path
templates_path = ['_templates']

# Patterns to ignore when looking for source files
exclude_patterns = []

# Language
language = 'fr'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'collapse_navigation': False,
    'prev_next_buttons_location': 'bottom',
}

# Output file base name for HTML help builder
htmlhelp_basename = 'MangetamainAnalyticsdoc'

# -- Options for Intersphinx -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'plotly': ('https://plotly.com/python-api-reference/', None),
}

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
