# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'agrifoodpy'
copyright = '2023, Juan P. Cordero'
author = 'Juan P. Cordero'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser', 'autoapi.extension', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ['_build/html/_static']


# -- Options for AutoAPI -----------------------------------------------------
autoapi_dirs = ['../agrifoodpy']
autoapi_options = [ 'members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members', ]
autoapi_ignore = ['*/tests*','*migrations*']

# Sphinx Gallery
extensions += ['sphinx_gallery.gen_gallery', ]
sphinx_gallery_conf = {
    'examples_dirs': '../examples',  # path to examples scripts
    'gallery_dirs': 'examples',      # path to gallery generated examples
    'run_stale_examples': True,
    'download_all_examples': False,
}