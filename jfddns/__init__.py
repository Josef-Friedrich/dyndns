from docutils.core import publish_string
from jfddns.config import load_config, validate_config
from jfddns.exceptions import JfErr, ParameterError
from jfddns.ipaddresses import IpAddresses
from jfddns.names import Names
import argparse
import flask
import inspect
import jfddns.dns as jf_dns
import logging
import os


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

app = flask.Flask(__name__)


logger = logging.getLogger('jfddns')
handler = logging.FileHandler('jfddns.log')
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def msg(text):
    logger.info(text)
    return text


def update_dns_record(secret=None, fqdn=None, zone_name=None, record_name=None,
                      ip_1=None, ip_2=None, ipv4=None, ipv6=None, config=None):

    """
    :param str secret: A password like secret string.
    :param str fqdn: The Fully-Qualified Domain Name
      (e. g. ``www.example.com``)
    :param str zone_name: The zone name (e. g. ``example.com``)
    :param str record_name: The record name (e. g. ``www``)
    :param str ip_1: A IP address, can be version 4 or version 6
    :param str ip_2: A second IP address, can be version 4 or version 6. Must
      be a different version than ``ip_1``.
    :param str ipv4: A IP address version 4
    :param str ipv6: A IP address version 6
    :param dict config: The configuration as a dictionary as return by the
      function ``validate_config()``.
    """

    if not config:
        config = load_config()

    config = validate_config(config)
    zones = config['zones']

    if str(secret) != str(config['secret']):
        raise JfErr('You specified a wrong secret key.')

    names = Names(zones, fqdn=fqdn, zone_name=zone_name,
                  record_name=record_name)

    ipaddresses = IpAddresses(ip_1=ip_1, ip_2=ip_2, ipv4=ipv4, ipv6=ipv6,
                              request=flask.request)

    update = jf_dns.DnsUpdate(
        nameserver=config['nameserver'],
        names=names,
        ipaddresses=ipaddresses,
    )
    results = update.update()

    out = []
    for result in results:
        out.append('{} fqdn: {} old_ip: {} new_ip: {}'.format(
            result['status'],
            names.fqdn,
            result['old_ip'],
            result['new_ip'],
        ))

    return msg(' | '.join(out))


def catch_errors(**kwargs):
    try:
        return update_dns_record(**kwargs)
    except JfErr as e:
        return msg('ERROR {}'.format(e))
    except ParameterError as e:
        return msg('ERROR {}'.format(e))


@app.route('/update-by-path/<secret>/<fqdn>')
@app.route('/update-by-path/<secret>/<fqdn>/<ip_1>')
@app.route('/update-by-path/<secret>/<fqdn>/<ip_1>/<ip_2>')
def update_by_path(secret, fqdn, ip_1=None, ip_2=None):
    return catch_errors(secret=secret, fqdn=fqdn, ip_1=ip_1, ip_2=ip_2)


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
            return msg('Unknown query string argument: "{}"'.format(key))

    return catch_errors(**input_args)


def rst_to_string(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    rst = open(path, 'r')
    return rst.read()


@app.route('/')
def index():
    config = False
    try:
        config = validate_config(load_config())
    except Exception:
        pass

    rst = rst_to_string('usage.rst')
    if not config:
        rst = rst_to_string('configuration.rst') + '\n\n' + rst

    return publish_string(rst, writer_name='html')


@app.route('/about')
def about():
    return 'jfddns (version: {})'.format(__version__)


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
