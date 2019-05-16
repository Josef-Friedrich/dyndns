"""A collection of HTML template functions."""

# standard imports
import os
import re

# third party imports
import docutils.core
import flask

# local imports
from dyndns._version import get_versions
from dyndns.config import get_config

VERSION = get_versions()['version']


class RestructuredText:

    @staticmethod
    def read(file_name):
        path = os.path.join(os.path.dirname(__file__), 'rst', file_name)
        rst = open(path, 'r')
        return rst.read()

    @staticmethod
    def remove_heading(restructured_text):
        return re.sub('^.*\n.*\n.*\n', '', restructured_text)

    @staticmethod
    def to_html(restructured_text, remove_heading=False):
        if remove_heading:
            restructured_text = RestructuredText.remove_heading(
                restructured_text
            )
        html = docutils.core.publish_parts(restructured_text,
                                           writer_name='html')
        return html['html_body']

    @staticmethod
    def read_to_html(file_name, remove_heading=False):
        rst = RestructuredText.read(file_name)
        return RestructuredText.to_html(rst, remove_heading)


def template_usage(remove_heading=False):
    config = False
    try:
        config = get_config()
    except Exception:
        pass

    usage = RestructuredText.read('usage.rst')

    if config and 'dyndns_domain' in config:
        usage = re.sub(r'``(<your-domain>.*)``', r'`\1 <\1>`_', usage)
        usage = usage.replace(
            '<your-domain>',
            'http://{}'.format(config['dyndns_domain'])
        )
    return RestructuredText.to_html(usage, remove_heading)


def template_base(title, content):
    return flask.render_template(
        'base.html',
        title=title,
        content=content,
        version=VERSION,
    )
