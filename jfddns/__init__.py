"""Initialize the Flask app."""

import docutils.core
from jfddns.config import get_config
from jfddns.exceptions import \
    ConfigurationError, \
    DNSServerError, \
    IpAddressesError, \
    NamesError, \
    ParameterError
from jfddns.ipaddresses import IpAddresses
from jfddns.log import msg, UpdatesDB
from jfddns.names import Names
import argparse
import flask
import inspect
import jfddns.dns as jf_dns
import os
import re


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

app = flask.Flask(__name__)


def authenticate(secret, config):
    if str(secret) != str(config['secret']):
        raise ParameterError('You specified a wrong secret key.')


def restructured_text_to_html(restructured_text):
    html = docutils.core.publish_parts(restructured_text, writer_name='html')
    return html['html_body']


def parameter_err(function, exception, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except exception as e:
        raise ParameterError(str(e))


def update_dns_record(secret=None, fqdn=None, zone_name=None, record_name=None,
                      ip_1=None, ip_2=None, ipv4=None, ipv6=None, ttl=None,
                      config=None):
    """
    Update a DNS record.

    :param str secret: A password like secret string. The secret string has to
      be at least 8 characters long and only alphnumeric characters are
      allowed.
    :param str fqdn: The Fully-Qualified Domain Name
      (e. g. ``www.example.com``). If you specify the argument ``fqdn``, you
      don’t have to specify the arguments ``zone_name`` and ``record_name``.
    :param str zone_name: The zone name (e. g. ``example.com``). You have to
      specify the argument ``record_name``.
    :param str record_name: The record name (e. g. ``www``). You have to
      specify the argument ``zone_name``.
    :param str ip_1: A IP address, can be version 4 or version 6.
    :param str ip_2: A second IP address, can be version 4 or version 6. Must
      be a different version than ``ip_1``.
    :param str ipv4: A IP address version 4.
    :param str ipv6: A IP address version 6.
    :param int ttl: Time to live.
    :param dict config: The configuration in the Python dictionary format
      (as returned by the function ``validate_config()``).
    """

    if not config:
        config = get_config()

    zones = config['zones']

    authenticate(secret, config)

    names = parameter_err(Names, NamesError, zones, fqdn=fqdn,
                          zone_name=zone_name, record_name=record_name)
    ipaddresses = parameter_err(IpAddresses, IpAddressesError, ip_1=ip_1,
                                ip_2=ip_2, ipv4=ipv4, ipv6=ipv6,
                                request=flask.request)

    update = jf_dns.DnsUpdate(
        nameserver=config['nameserver'],
        names=names,
        ipaddresses=ipaddresses,
        ttl=ttl,
    )
    results = update.update()

    messages = []
    for result in results:
        message = 'fqdn: {} old_ip: {} new_ip: {}'.format(
            names.fqdn,
            result['old_ip'],
            result['new_ip'],
        )
        messages.append(msg(message, result['status']))

    return ''.join(messages)


def delete_dns_record(secret=None, fqdn=None, config=None):
    if not config:
        config = get_config()
    zones = config['zones']

    authenticate(secret, config)

    names = parameter_err(Names, NamesError, zones, fqdn=fqdn)

    delete = jf_dns.DnsUpdate(
        nameserver=config['nameserver'],
        names=names,
    )

    if delete.delete():
        return msg('Deleted "{}".'.format(names.fqdn), 'UPDATED')
    else:
        return msg('Deletion not successful "{}".'.format(names.fqdn),
                   'UNCHANGED')


def catch_errors(function, **kwargs):
    try:
        return function(**kwargs)
    except ParameterError as error:
        return msg(str(error), 'PARAMETER_ERROR')
    except ConfigurationError as error:
        return msg(str(error), 'CONFIGURATION_ERROR')
    except DNSServerError as error:
        return msg(str(error), 'DNS_SERVER_ERROR')


@app.route('/update-by-path/<secret>/<fqdn>')
@app.route('/update-by-path/<secret>/<fqdn>/<ip_1>')
@app.route('/update-by-path/<secret>/<fqdn>/<ip_1>/<ip_2>')
def update_by_path(secret, fqdn, ip_1=None, ip_2=None):
    return catch_errors(update_dns_record, secret=secret, fqdn=fqdn, ip_1=ip_1,
                        ip_2=ip_2)


@app.route('/update-by-query')
def update_by_query_string():
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
                'PARAMETER_ERROR',
            )

    return catch_errors(update_dns_record, **input_args)


@app.route('/delete-by-path/<secret>/<fqdn>')
def delete_by_path(secret, fqdn, ip_1=None, ip_2=None):
    return catch_errors(delete_dns_record, secret=secret, fqdn=fqdn)


def read_restructured_text_file(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    rst = open(path, 'r')
    return rst.read()


def rst_about():
    return '`jfddns <https://pypi.org/project/jfddns>`_  (version: {})' \
           .format(__version__)


@app.route('/')
def index():
    config = False
    try:
        config = get_config()
    except Exception:
        pass

    out = read_restructured_text_file('usage.rst')

    if config and 'jfddns_domain' in config:
        out = re.sub(r'``(<your-domain>.*)``', r'`\1 <\1>`_', out)
        out = out.replace(
            '<your-domain>',
            'http://{}'.format(config['jfddns_domain'])
        )

    if not config:
        out = read_restructured_text_file('configuration.rst') + '\n\n' + out

    content = restructured_text_to_html(out + '\n\nAbout\n-----\n\n' +
                                        rst_about())
    return flask.render_template('base.html', title='jfddns',
                                 content=content)


@app.route('/about')
def about():
    about = rst_about()
    return flask.render_template('base.html', title='About',
                                 content=restructured_text_to_html(about))


@app.route('/statistics')
def statistics():
    try:
        config = get_config()
    except Exception:
        pass

    def has_record(fqdn, config):
        names = Names(config['zones'], fqdn=fqdn)
        update = jf_dns.DnsUpdate(
            nameserver=config['nameserver'],
            names=names,
        )
        return update._resolve(4)

    db = UpdatesDB()

    out = []
    for fqdn in db.get_fqdns():
        if has_record(fqdn, config):
            rows = db.get_updates_by_fqdn_dict(fqdn)
            table = flask.render_template('fqdn-table.html', fqdn=fqdn,
                                          rows=rows)
            out.append(table)

    return flask.render_template('base.html', title='Statistics',
                                 content='\n'.join(out))


@app.route('/last-updates')
def last_updates():
    db = UpdatesDB()
    db.log_update(True, 'c.example.com', 'a', '1.2.3.4')
    db.log_update(False, 'c.example.com', 'a', '1.2.3.4')
    db.log_update(True, 'c.example.com', 'a', '2.2.3.4')
    db.log_update(True, 'c.example.com', 'a', '3.2.3.4')
    db.log_update(True, 'c.example.com', 'aaaa', '1::2')
    db.log_update(True, 'c.example.com', 'aaaa', '1::3')
    db.log_update(True, 'b.example.com', 'a', '1.2.3.4')
    db.log_update(False, 'b.example.com', 'a', '1.2.3.4')
    db.log_update(True, 'a.example.com', 'a', '1.2.3.4')
    db.log_update(True, 'a.example.com', 'a', '1.2.3.3')
    db.log_update(True, 'a.example.com', 'a', '1.2.3.2')
    db.log_update(False, 'a.example.com', 'a', '1.2.3.2')
    results = []
    db.cursor.execute('SELECT * FROM updates ORDER BY update_time LIMIT 25;')
    rows = db.cursor.fetchall()

    for row in rows:
        results.append(db.normalize_row(row))

    content = flask.render_template('table-last-updates.html', rows=results)
    return flask.render_template('base.html', title='Last updates',
                                 content=content)


def get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=54321)
    parser.add_argument('-c', '--config-file')

    return parser


def debug():
    args = get_argparser().parse_args()
    if hasattr(args, 'config_file'):
        global config_file
        config_file = args.config_file
    app.run(debug=True, port=args.port)


if __name__ == "__main__":
    app.run(debug=True)
