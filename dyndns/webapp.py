"""Initialize the Flask app."""

from __future__ import annotations

import inspect
import logging
from typing import Any

import flask

from dyndns.dns_updates import delete_dns_record, update_dns_record
from dyndns.exceptions import ParameterError
from dyndns.manager import get_manager

app = flask.Flask(__name__)


log = logging.getLogger("werkzeug")
# log.disabled = True
log.setLevel(logging.WARNING)


@app.errorhandler(Exception)
def handle_exception(e: Exception) -> tuple[str, int]:
    # https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    status_code: int = 500
    if hasattr(e, "status_code"):
        status_code = getattr(e, "status_code")
    else:
        status_code = 500

    log_level: str
    if hasattr(e, "log_level"):
        log_level = getattr(e, "log_level").name
    else:
        log_level = e.__class__.__name__.upper()

    return f"{log_level}: {e}\n", status_code


@app.route("/")
def home() -> str:
    return "dyndns"


@app.route("/check")
def check() -> str:
    return get_manager().check()


@app.route("/update-by-path/<secret>/<fqdn>")
@app.route("/update-by-path/<secret>/<fqdn>/<ip_1>")
@app.route("/update-by-path/<secret>/<fqdn>/<ip_1>/<ip_2>")
def update_by_path(
    secret: str, fqdn: str, ip_1: str | None = None, ip_2: str | None = None
) -> str:
    return update_dns_record(secret=secret, fqdn=fqdn, ip_1=ip_1, ip_2=ip_2)


@app.route("/update-by-query")
def update_by_query_string() -> str:
    args = flask.request.args
    # Returns ImmutableMultiDict([('secret', '12345678'), ...])
    # dict(args):
    # {'secret': ['12345678'],

    kwargs = inspect.getfullargspec(update_dns_record).args

    input_args: Any = {}
    for key, arg in args.items():
        input_args[key] = arg

        if key not in kwargs:
            raise ParameterError(
                f'Unknown query string argument: "{key}"',
            )
    return update_dns_record(**input_args)


@app.route("/delete-by-path/<secret>/<fqdn>")
def delete_by_path(secret: str, fqdn: str) -> str:
    return delete_dns_record(secret=secret, fqdn=fqdn)


if __name__ == "__main__":
    app.run()
