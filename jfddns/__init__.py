import argparse
import dns.name
import dns.query
import dns.tsigkeyring
import dns.update
import flask
import ipaddress
import re
import yaml

app = flask.Flask(__name__)
config_path = '/etc/jfddns.yml'
usage_text = 'Usage: ?secret=<secret>&zone=<zone>&record=<record>&' + \
             'ipv6=<ipv6>&ipv4=<ipv4>'


class DnsUpdate(object):

    def __init__(self, nameserver, zone, key):
        keyring = {}
        keyring[str(dns.name.from_text(zone))] = key
        self.keyring = dns.tsigkeyring.from_text(keyring)
        self.dns_update = dns.update.Update(zone, keyring=self.keyring)
        self.nameserver = nameserver

    def set_record(self, record, ip, ip_version=4):
        self.dns_update.delete(record)
        if ip_version == 4:
            record_type = 'a'
        elif ip_version == 6:
            record_type = 'aaaa'
        else:
            raise ValueError('“ip_version” must be 4 or 6')

        self.dns_update.add(record, 300, record_type, ip)
        dns.query.tcp(self.dns_update, self.nameserver)


class Validate(object):

    @staticmethod
    def ipv4(address):
        address = ipaddress.ip_address(address)
        if address.version == 4:
            return address
        else:
            raise ValueError('Not a valid ipv4 address.')

    @staticmethod
    def ipv6(address):
        address = ipaddress.ip_address(address)
        if address.version == 6:
            return address
        else:
            raise ValueError('Not a valid ipv6 address.')

    @staticmethod
    def _hostname(hostname):
        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        if len(hostname) > 253:
            return False

        labels = hostname.split(".")

        # the TLD must be not all-numeric
        if re.match(r"[0-9]+$", labels[-1]):
            return False

        allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(label) for label in labels)

    def zone(self, zone_name):
        if self._hostname(zone_name):
            return zone_name
        else:
            raise ValueError('invalid zone_name')

    def record(self, record_name):
        if self._hostname(record_name):
            return record_name
        else:
            raise ValueError('invalid record_name')


def load_config(path):
    stream = open(path, 'r')
    config = yaml.load(stream)
    stream.close()
    return config


def get_zone_tsig(zone_name, config):
    for zone in config['zones']:
        if zone['zone'] == zone_name:
            return zone['key']

    raise ValueError('Zone key couldn’t be found.')


def validate_args(args, config):
    if 'record' not in args and 'zone' not in args and 'secret' not in args:
        raise ValueError(usage_text)
    if 'ipv4' not in args and 'ipv6' not in args:
        raise ValueError(usage_text)

    if args['secret'] != str(config['secret']):
        raise ValueError('Wrong secret')

    v = Validate()

    if 'ipv4' in args:
        ipv4 = str(v.ipv4(args['ipv4']))
    else:
        ipv4 = None

    if 'ipv6' in args:
        ipv6 = str(v.ipv6(args['ipv6']))
    else:
        ipv6 = None

    return {
        'zone': v.zone(args['zone']),
        'record': v.record(args['record']),
        'ipv4': ipv4,
        'ipv6': ipv6,
    }


@app.route("/")
def update():

    config = load_config(config_path)
    input_args = validate_args(flask.request.args, config)

    dns_update = DnsUpdate(
        config['nameserver'],
        input_args['zone'],
        get_zone_tsig(input_args['zone'], config),
    )

    if input_args['ipv4']:
        dns_update.set_record(input_args['record'], input_args['ipv4'], 4)

    if input_args['ipv6']:
        dns_update.set_record(input_args['record'], input_args['ipv6'], 6)

    return 'ok'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple dynamic DNS update HTTP based API using python '
        'and the flask web framework.'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=5000,
    )

    return parser


def main():
    args = parse_args().parse_args()
    app.run(port=args.port, debug=False)


if __name__ == "__main__":
    app.run(debug=True)
