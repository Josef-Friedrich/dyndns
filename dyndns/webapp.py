"""Initialize the Flask app."""

from __future__ import annotations

import inspect

import flask

from dyndns.config import get_config
from dyndns.dns_updates import catch_errors, delete_dns_record, update_dns_record
from dyndns.html_template import RestructuredText, template_base, template_usage
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


@app.route("/")
def home():
    config = False
    try:
        config = get_config()
    except Exception:
        pass

    if not config:
        configuration = RestructuredText.read_to_html("configuration.rst")
    else:
        configuration = ""

    content = flask.render_template(
        "home.html",
        usage=template_usage(),
        configuration=configuration,
        about=RestructuredText.read_to_html("about.rst"),
    )
    return template_base("dyndns", content)


@app.route("/about")
def about() -> str:
    return template_base(
        "About",
        RestructuredText.read_to_html("about.rst", remove_heading=True),
    )


@app.route("/docs/installation")
def docs_installation() -> str:
    return template_base(
        "Installation",
        RestructuredText.read_to_html("installation.rst", remove_heading=True),
    )


@app.route("/docs/configuration")
def docs_configuration() -> str:
    return template_base(
        "Configuration",
        RestructuredText.read_to_html("configuration.rst", remove_heading=True),
    )


@app.route("/docs/usage")
def docs_usage() -> str:
    return template_base("Usage", template_usage(remove_heading=True))


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
