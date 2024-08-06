"""Initialize the Flask app."""

from __future__ import annotations

import inspect

import flask

from dyndns.dns_updates import catch_errors, delete_dns_record, update_dns_record
from dyndns.html_template import template_base
from dyndns.log import Update, UpdatesDB, msg

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
            return msg(
                'Unknown query string argument: "{}"'.format(key),
                "PARAMETER_ERROR",
            )

    return catch_errors(update_dns_record, **input_args)


@app.route("/delete-by-path/<secret>/<fqdn>")
def delete_by_path(secret: str, fqdn: str) -> str:
    return catch_errors(delete_dns_record, secret=secret, fqdn=fqdn)


@app.route("/statistics/updates-by-fqdn")
def statistics_updates_by_fqdn() -> str:
    db = UpdatesDB()

    out: list[str] = []
    for fqdn in db.get_fqdns():
        rows = db.get_updates_by_fqdn(fqdn)
        table: str = flask.render_template(
            "table-updates-by-fqdn.html", fqdn=fqdn, rows=rows
        )
        out.append(table)

    return template_base("Updates by FQDN", "\n".join(out))


@app.route("/statistics/latest-submissions")
def statistics_latest_submissions() -> str:
    db = UpdatesDB()
    results: list[Update] = []
    db.cursor.execute("SELECT * FROM updates ORDER BY update_time DESC " "LIMIT 50;")
    rows = db.cursor.fetchall()

    for row in rows:
        results.append(db.normalize_row(row))

    content: str = flask.render_template("table-latest-submissions.html", rows=results)
    return template_base("Latest submissions", content)


if __name__ == "__main__":
    app.run()
