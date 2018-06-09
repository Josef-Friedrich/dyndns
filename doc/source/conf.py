import sphinx_rtd_theme
import jfddns

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'jfddns'
copyright = u'2018, Josef Friedrich'
author = u'Josef Friedrich'
version = jfddns.__version__
release = jfddns.__version__
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

autodoc_default_flags = ['members', 'undoc-members', 'private-members', 'show-inheritance']

html_static_path = []
htmlhelp_basename = 'jfddnsdoc'

[extensions]
todo_include_todos = True
