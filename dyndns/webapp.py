"""Initialize the Flask app."""

from __future__ import annotations

import inspect

import flask

from dyndns.dns_updates import catch_errors, delete_dns_record, update_dns_record
from dyndns.log import logger

app = flask.Flask(__name__)


@app.route("/update-by-path/<secret>/<fqdn>")
@app.route("/update-by-path/<secret>/<fqdn>/<ip_1>")
@app.route("/update-by-path/<secret>/<fqdn>/<ip_1>/<ip_2>")
def update_by_path(
    secret: str, fqdn: str, ip_1: str | None = None, ip_2: str | None = None
) -> str:
    return catch_errors(
        update_dns_record, secret=secret, fqdn=fqdn, ip_1=ip_1, ip_2=ip_2
    )


@app.route("/update-by-query")
def update_by_query_string() -> str:
    args = flask.request.args
    # Returns ImmutableMultiDict([('secret', '12345678'), ...])
    # dict(args):
    # {'secret': ['12345678'],

    kwargs = inspect.getfullargspec(update_dns_record).args

    input_args = {}
    for key, arg in args.items():
        input_args[key] = arg

        if key not in kwargs:
            return logger.log(
                'Unknown query string argument: "{}"'.format(key),
                "PARAMETER_ERROR",
            )

    return catch_errors(update_dns_record, **input_args)


@app.route("/delete-by-path/<secret>/<fqdn>")
def delete_by_path(secret: str, fqdn: str) -> str:
    return catch_errors(delete_dns_record, secret=secret, fqdn=fqdn)


if __name__ == "__main__":
    app.run()
