from jfddns import validate
import argparse
import flask
import jfddns.dns as jf_dns
import logging
import os
import re
import yaml

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


def load_config():
    config_files = []
    if 'JFDDNS_CONFIG_FILE' in os.environ:
        config_files.append(os.environ['JFDDNS_CONFIG_FILE'])
    config_files.append(os.path.join(os.getcwd(), '.jfddns.yml'))
    config_files.append('/etc/jfddns.yml')

    config_file = False

    for _config_file in config_files:
        if os.path.exists(_config_file):
            config_file = _config_file
            break

    if not config_file:
        return False

    stream = open(config_file, 'r')
    config = yaml.load(stream)
    stream.close()
    return config


def msg(text):
    logger.info(text)
    return text


def update_dns_record(secret=None, fqdn=None, zone_name=None, record_name=None,
                      ip_1=None, ip_2=None, config=None):

    ##
    # config
    ##

    if not config:
        try:
            config = load_config()
        except IOError:
            return msg('The configuration file could not be found.')
        except yaml.error.YAMLError:
            return msg('The configuration file is in a invalid YAML format.')

    if not config:
        return msg('The configuration file could not be found.')

    if 'secret' not in config:
        return msg('Your configuration must have a "secret" key, for example: '
                   '"secret: VDEdxeTKH"')

    if not validate.secret(config['secret']):
        return msg('The secret must be at least 8 characters long and may not '
                   'contain any non-alpha-numeric characters.')

    if 'nameserver' not in config:
        return msg('Your configuration must have a "nameserver" key, '
                   'for example: "nameserver: 127.0.0.1"')

    # zones

    if 'zones' not in config:
        return msg('Your configuration must have a "zones" key.')

    if not isinstance(config['zones'], (list,)):
        return msg('Your "zones" key must contain a list of zones.')

    if len(config['zones']) < 1:
        return msg('You must have at least one zone configured, for example:'
                   '"- name: example.com" and "twig_key: tPyvZA=="')

    for _zone in config['zones']:
        if 'name' not in _zone:
            return msg('Your zone dictionary must contain a key "name"')

        if not validate.zone(_zone['name']):
            return msg('Invalid zone name: {}'.format(_zone['name']))

        if 'tsig_key' not in _zone:
            return msg('Your zone dictionary must contain a key "tsig_key"')

        if not validate.tsig_key(_zone['tsig_key']):
            return msg('Invalid tsig key: {}'.format(_zone['tsig_key']))

    ##
    # secret
    ##

    if str(secret) != str(config['secret']):
        return msg('You specified a wrong secret key.')

    ##
    # fqdn zone_name record_name
    ##

    if fqdn and zone_name and record_name:
        return msg('Specify “fqdn” or "zone_name" and "record_name".')

    zones = jf_dns.Zones(config['zones'])

    if fqdn:
        record_name, zone_name = zones.split_fqdn(fqdn)

    if not record_name:
        return msg('Value "record_name" is required.')

    if not zone_name:
        return msg('Value "zone_name" is required.')

    ##
    # ip
    ##

    if ip_1:
        ip_1 = validate.ip(ip_1)
        if not ip_1:
            return msg('"ip_1" is not a valid IP address.')

    if ip_2:
        ip_2 = validate.ip(ip_2)
        if not ip_2:
            return msg('"ip_2" is not a valid IP address.')

    if ip_1 and ip_2 and ip_1[1] == ip_2[1]:
        return msg('"ip_1" and "ip_2" using the same ip version.')

    ##
    # dns update
    ##

    update = jf_dns.DnsUpdate(
        nameserver=config['nameserver'],
        zone_name=zone_name,
        tsig_key=zones.get_tsig_key(zone_name),
        record_name=record_name,
    )

    if not fqdn:
        fqdn = update._build_fqdn(update.record_name)
        fqdn = re.sub('\.$', '', str(fqdn))

    if ip_1:
        setattr(update, 'ipv{}'.format(ip_1[1]), ip_1[0])
    if ip_2:
        setattr(update, 'ipv{}'.format(ip_2[1]), ip_2[0])

    results = update.update()

    out = []
    for result in results:
        out.append('{} fqdn: {} old_ip: {} new_ip: {}'.format(
            result['status'],
            fqdn,
            result['old_ip'],
            result['new_ip'],
        ))

    return msg(' | '.join(out))


@app.route('/update/<secret>/<fqdn>')
@app.route('/update/<secret>/<fqdn>/<ip_1>')
@app.route('/update/<secret>/<fqdn>/<ip_1>/<ip_2>')
def update_by_path(secret, fqdn, ip_1=None, ip_2=None):
    return update_dns_record(secret=secret, fqdn=fqdn, ip_1=ip_1, ip_2=ip_2)


@app.route('/')
def update_by_query_string():
    args = flask.request.args
    return update_dns_record(
        secret=args['secret'],
        zone_name=args['zone'],
        record_name=args['record'],
        ip_1=args['ipv4']
    )


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
