# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PEPFlow"
copyright = "2025, PEPFlow Contributors"
author = "PEPFlow Contributors"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "nbsphinx",
    "myst_nb",
    "sphinx_copybutton",
    "sphinx_togglebutton",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
# html_logo = "pepflow-logo.svg"
html_title = "PEPFlow"
html_favicon = "_static/pepflow-favicon.ico"
html_theme_options = {
    "navbar_end": ["icon-links", "theme-switcher"],
    "logo": {
        "image_light": "pepflow-logo.svg",
        "image_dark": "pepflow-logo.svg",
        "text": "PEPFlow",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/BichengYing/PEPFlow",
            "icon": "fab fa-github",
            "type": "fontawesome",
        },
    ],
    "secondary_sidebar_items": ["page-toc"],
}
html_sidebars = {
    "**": []  # no sidebar for any page
}

myst_enable_extensions = [
    "dollarmath",  # $...$, $$...$$
    "amsmath",  # align environment
]

# Tell Sphinx how to parse .md files
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "myst-nb",
}

# Only toggle containers right after H2/H3 headings:
# togglebutton_selector = "h1 + . fold, h2 + .fold, h3 + .fold"
# togglebutton_hint = "Click to expand"
# togglebutton_open_current = True


def setup(app):
    app.add_css_file("custom.css")


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_param = False
napoleon_use_rtype = False
napoleon_use_ivar = True
