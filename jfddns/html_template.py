"""A collection of HTML template functions."""

from jfddns._version import get_versions
import docutils.core
import flask
import os
import re

version = get_versions()['version']


class RestructuredText(object):

    @staticmethod
    def read(file_name):
        path = os.path.join(os.path.dirname(__file__), 'rst', file_name)
        rst = open(path, 'r')
        return rst.read()

    @staticmethod
    def to_html(restructured_text):
        html = docutils.core.publish_parts(restructured_text,
                                           writer_name='html')
        return html['html_body']

    @staticmethod
    def remove_heading(restructured_text):
        return re.sub('^.*\n.*\n.*\n', '', restructured_text)

    @staticmethod
    def read_to_html(file_name, remove_heading=False):
        rst = RestructuredText.read(file_name)
        if remove_heading:
            rst = RestructuredText.remove_heading(rst)
        return RestructuredText.to_html(rst)


def rst_about():
    return '`jfddns <https://pypi.org/project/jfddns>`_  (version: {})' \
           .format(version)


def template_base(title, content):
    return flask.render_template(
        'base.html',
        title=title,
        content=content,
        version=version,
    )


def template_rst_file(file_name):
    return RestructuredText.read_to_html(file_name, remove_heading=True)
