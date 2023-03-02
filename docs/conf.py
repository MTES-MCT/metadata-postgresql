# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('../.'))

from plume.config import PLUME_VERSION


# -- Project information -----------------------------------------------------

project = 'Plume'
copyright = '2023, République française'
author = "Didier Leclerc et Leslie Lemaire, Direction du numérique du Ministère de la Transition écologique et de la Cohésion des territoires, du Ministère de la Transition énergétique et du Secrétariat d'État chargé de la Mer"

# The full version, including alpha/beta/rc tags
release = PLUME_VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.githubpages',
    'myst_parser', # Markdown support
    'sphinx.ext.autodoc',
    'numpydoc' # NumPy support
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']
templates_path = []

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'fr'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '**/tests',
    '**/__save__',
    'plume/*.py',
    'plume/bibli_install',
    'plume/i18n',
    'postgresql',
    '_build'
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            # URL where the link will redirect
            "url": "https://github.com/MTES-MCT/metadata-postgresql",  # required
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        }
   ]
}

html_logo = html_favicon = '../plume/icons/logo/plume.svg'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
html_static_path = []


# -- Myst options -------------------------------------------------------------

## Markdown support
## See docs : https://myst-parser.readthedocs.io/en/latest/syntax/optional.html

myst_heading_anchors = 5

