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

project = u'dyndns'
copyright = u'2018, Josef Friedrich'
author = u'Josef Friedrich'
version = dyndns.__version__
release = dyndns.__version__
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

autodoc_default_flags = ['members', 'undoc-members', 'private-members', 'show-inheritance']

html_static_path = []
htmlhelp_basename = 'dyndnsdoc'

[extensions]
todo_include_todos = True
