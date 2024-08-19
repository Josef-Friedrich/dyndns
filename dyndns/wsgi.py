"""https://flask.palletsprojects.com/en/3.0.x/deploying/uwsgi/"""

from flask import Flask

from dyndns.environment import ConfiguredEnvironment
from dyndns.webapp import create_app

app: Flask = create_app(ConfiguredEnvironment())
