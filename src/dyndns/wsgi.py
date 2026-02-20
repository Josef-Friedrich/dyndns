"""
We’re using the app factory pattern, so we need to create a `small Python
file <https://flask.palletsprojects.com/en/3.0.x/deploying/uwsgi/>`_  to create the app,
then point uWSGI at that.
"""

from flask import Flask

from dyndns.environment import ConfiguredEnvironment
from dyndns.webapp import create_app

app: Flask = create_app(ConfiguredEnvironment())
