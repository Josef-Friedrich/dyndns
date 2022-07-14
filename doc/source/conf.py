import sphinx_rtd_theme

import dyndns

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = []
extensions += ['sphinx.ext.autodoc']
extensions += ['sphinx.ext.todo']
extensions += ['sphinx.ext.viewcode']
extensions += ['sphinxarg.ext']

templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = 'dyndns'
copyright = '2018-2021, Josef Friedrich'
author = 'Josef Friedrich'
version = dyndns.__version__
release = dyndns.__version__
language = 'en'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '',
    'show-inheritance': True,
}

html_static_path = []
htmlhelp_basename = 'dyndnsdoc'

[extensions]
todo_include_todos = True
