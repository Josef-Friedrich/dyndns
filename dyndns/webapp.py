"""Initialize the Flask app."""

from __future__ import annotations

import logging
from typing import Any, Optional

import flask
from pydantic import BaseModel

from dyndns.environment import ConfiguredEnvironment


class UpdateQueryParams(BaseModel):
    secret: str
    fqdn: Optional[str] = None
    zone_name: Optional[str] = None
    record_name: Optional[str] = None
    ip_1: Optional[str] = None
    ip_2: Optional[str] = None
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    ttl: Optional[int] = None


def create_app(env: ConfiguredEnvironment) -> flask.Flask:
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
        return env.check()

    @app.route("/update-by-path/<secret>/<fqdn>")
    @app.route("/update-by-path/<secret>/<fqdn>/<ip_1>")
    @app.route("/update-by-path/<secret>/<fqdn>/<ip_1>/<ip_2>")
    def update_by_path(
        secret: str, fqdn: str, ip_1: str | None = None, ip_2: str | None = None
    ) -> str:
        env.authenticate(secret)
        return env.update_dns_record(fqdn=fqdn, ip_1=ip_1, ip_2=ip_2)

    @app.route("/update-by-query")
    def update_by_query_string() -> str:
        args: Any = flask.request.args.to_dict()

        params = UpdateQueryParams(**args)

        env.authenticate(params.secret)
        return env.update_dns_record(
            fqdn=params.fqdn,
            zone_name=params.zone_name,
            record_name=params.record_name,
            ip_1=params.ip_1,
            ip_2=params.ip_2,
            ipv4=params.ipv4,
            ipv6=params.ipv6,
            ttl=params.ttl,
        )

    @app.route("/delete-by-path/<secret>/<fqdn>")
    def delete_by_path(secret: str, fqdn: str) -> str:
        env.authenticate(secret)
        return env.delete_dns_record(fqdn=fqdn)

    return app


if __name__ == "__main__":
    create_app(ConfiguredEnvironment()).run()
