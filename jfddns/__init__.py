from jfddns import validate
import jfddns.dns as jf_dns
import argparse
import dns.name
import dns.query
import dns.resolver
import dns.tsigkeyring
import dns.update
import flask
import logging
import os
import yaml

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

app = flask.Flask(__name__)
config_file = '/etc/jfddns.yml'
usage_text = 'Usage: ?secret=<secret>&zone=<zone>&record=<record>&' + \
             'ipv6=<ipv6>&ipv4=<ipv4>'


logger = logging.getLogger('jfddns')
handler = logging.FileHandler('jfddns.log')
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def normalize_dns_name(name):
    return str(dns.name.from_text(name))


def split_hostname(hostname, zones):
    """Split hostname into record_name and zone_name
    for example: www.example.com -> www. example.com.
    """
    hostname = normalize_dns_name(hostname)
    for zone in zones:
        zone_name = zone['zone']
        zone_name = normalize_dns_name(zone_name)
        record_name = hostname.replace(zone_name, '')
        if len(record_name) > 0 and len(record_name) < len(hostname):
            return (record_name, zone_name)


class DnsUpdate(object):

    def __init__(self, nameserver, zone, key):
        self.nameserver = nameserver
        self.zone = dns.name.from_text(zone)
        keyring = {}
        keyring[str(self.zone)] = key
        self.keyring = dns.tsigkeyring.from_text(keyring)
        self.dns_update = dns.update.Update(self.zone, keyring=self.keyring)

    def _concatenate(self, record_name):
        return dns.name.from_text('{}.{}'.format(record_name, self.zone))

    @staticmethod
    def _convert_record_type(ip_version=4):
        if ip_version == 4:
            return 'a'
        elif ip_version == 6:
            return 'aaaa'
        else:
            raise ValueError('“ip_version” must be 4 or 6')

    def _resolve(self, record_name, ip_version=4):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.nameserver]
        return str(resolver.query(self._concatenate(record_name),
                                  self._convert_record_type(ip_version))[0])

    def set_record(self, record_name, new_ip, ip_version=4):
        out = {}
        old_ip = self._resolve(record_name, ip_version)
        if new_ip == old_ip:
            out['old_ip'] = old_ip
        else:
            self.dns_update.delete(record_name)
            self.dns_update.add(record_name, 300,
                                self._convert_record_type(ip_version), new_ip)
            dns.query.tcp(self.dns_update, self.nameserver)
            checked_ip = self._resolve(record_name, ip_version)

            if new_ip != checked_ip:
                out['message'] = 'The DNS record couldn’t be updated.'
            else:
                out['new_ip'] = new_ip

        return out


def load_config(path):
    stream = open(path, 'r')
    config = yaml.load(stream)
    stream.close()
    return config


def get_zone_tsig(zone_name, config):
    for zone in config['zones']:
        if zone['zone'] == zone_name:
            return zone['key']


def message(text):
    return {'message': text}


def msg(text):
    logger.info(text)
    return text


def update_message(update_result):
    if 'message' in update_result:
        return update_result['message']
    elif 'old_ip' in update_result:
        return 'The ip address {} did not change.'.format(
            update_result['old_ip']
        )
    elif 'new_ip' in update_result:
        return 'The new ip address {} have been updated successfully.'.format(
            update_result['new_ip']
        )


def validate_args(args, config):
    if 'record' not in args and 'zone' not in args and 'secret' not in args:
        return message('The arguments “record”, “zone” and “secret” are ' +
                       'required.')
    if 'ipv4' not in args and 'ipv6' not in args:
        return message('The argument “ipv4” or the argument “ipv6” is '
                       'required.')
    if args['secret'] != str(config['secret']):
        return message('You specified a wrong secret key.')

    if 'ipv4' in args:
        ipv4 = validate.ipv4(args['ipv4'])
        if not ipv4:
            return message('Invalid ipv4 address.')
        else:
            ipv4 = str(ipv4)
    else:
        ipv4 = None

    if 'ipv6' in args:
        ipv6 = validate.ipv6(args['ipv6'])
        if not ipv6:
            return message('Invalid ipv6 address.')
        else:
            ipv6 = str(ipv6)
    else:
        ipv6 = None

    zone = validate.zone(args['zone'])
    if not zone:
        return message('Invalid zone string.')

    record = validate.zone(args['record'])
    if not record:
        return message('Invalid record string.')

    return {
        'zone': zone,
        'record': record,
        'ipv4': ipv4,
        'ipv6': ipv6,
    }


def update_dns_record(secret=None, fqdn=None, zone_name=None, record_name=None,
                      ip_1=None, ip_2=None, config=None):

    ##
    # config
    ##

    if not config:
        try:
            config = load_config(config_file)
        except IOError:
            return msg('The configuration file {} could not be found.'.format(
                config_file
            ))
        except yaml.error.YAMLError:
            return msg('The configuration file is in a invalid YAML format.')

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

    jf_dns.DnsUpdate(
        nameserver=config['nameserver'],
        zone_name=zone_name,
        tsig_key='lol'
    )


@app.route('/update/<secret>/<fqdn>')
@app.route('/update/<secret>/<fqdn>/<ip_1>')
@app.route('/update/<secret>/<fqdn>/<ip_1>/<ip_2>')
def update_by_path(secret, fqdn, ip_1=None, ip_2=None):
    update_dns_record(secret=secret, fqdn=fqdn, ip_1=ip_1, ip_2=ip_2)
    return 'ok'


@app.route("/")
def update():

    if not os.path.exists(config_file):
        return msg('The configuration file {} could not be found.'.format(
            config_file
        ))

    config = load_config(config_file)
    input_args = validate_args(flask.request.args, config)

    if 'message' in input_args:
        return msg(input_args['message'])

    key = get_zone_tsig(input_args['zone'], config)
    if not key:
        return msg('Zone key couldn’t be found.')

    dns_update = DnsUpdate(
        config['nameserver'],
        input_args['zone'],
        key,
    )

    out = []
    if input_args['ipv4']:
        result_ipv4 = dns_update.set_record(input_args['record'],
                                            input_args['ipv4'], 4)
        out.append('ipv4: ' + update_message(result_ipv4))

    if input_args['ipv6']:
        result_ipv6 = dns_update.set_record(input_args['record'],
                                            input_args['ipv6'], 6)
        out.append('ipv6: ' + update_message(result_ipv6))

    return msg(' '.join(out))


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
