
import yaml
from flask import abort
from flask import Flask
from flask import request
import dns.name
import dns.query
import dns.tsigkeyring
import dns.update
import ipaddress


config_path = '/etc/jfddns.yml'

usage_text = 'Usage: ?secret=<secret>&zone=<zone>&record=<record>&' + \
             'ipv6=<ipv6>&ipv4=<ipv4>'

def load_config(path):
    stream = open(path, 'r')
    config = yaml.load(stream)
    stream.close()
    return config


DOMAIN = 'jf-dyndns.cf'

app = Flask(__name__)


class DnsUpdate(object):

    def __init__(self, nameserver, zone, key):
        self.keyring = dns.tsigkeyring.from_text({
            'updatekey.': key
        })
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
    def zone(zone_name):
        return dns.name.from_text(zone_name)

    @staticmethod
    def record(record_name):
        return dns.name.from_text(record_name)


def get_zone_tsig(zone_name, config):
    for zone in config['zones']:
        if zone['zone'] == zone_name:
            return zone['key']

    raise ValueError('Zone key couldn’t be found.')


def validate_args(args, config):
    if 'record' not in args and 'zone' not in args and 'secret' not in args:
        raise ValueError(usage_text)
    if 'ipv4' not in args or 'ipv6' not in args:
        raise ValueError(usage_text)

    if args['secret'] != config['secret']:
        raise ValueError('Wrong secret')

    v = Validate()

    if 'ipv4' in args:
        ipv4 = v.ipv4(args['ipv4'])
    else:
        ipv4 = None

    if 'ipv6' in args:
        ipv6 = v.ipv6(args['ipv6'])
    else:
        ipv6 = None

    return {
        'zone': v.zone(args['zone']),
        'record': v.record(args['record']),
        'ipv4': ipv4,
        'ipv6': ipv6,
    }


def usage():
    return 'Usage: secret=<secret>&zone=<zone>&record=<record>&' + \
           'ipv6=<ipv6>&ipv4=<ipv4>'


@app.route("/")
def update():

    config = load_config(config_path)
    input_args = validate_args(request.args, config)

    dns_update = DnsUpdate(
        config['nameserver'],
        input_args['zone'],
        get_zone_tsig(input_args['zone'], config),
    )

    if input['ipv4']:
        dns_update.set_record(input_args['record'], input_args['ipv4'], 4)

    if input['ipv6']:
        dns_update.set_record(input_args['record'], input_args['ipv6'], 6)

    # record = dns.name.from_text(request.args['record'])
    # print(record)
    # domain = dns.name.from_text(DOMAIN)
    # particle = record.relativize(domain)
    # if not record.is_subdomain(domain):
    #     return 'nohost'
    #
    # if response.rcode() == 0:
    #     return "good "+str(request.args['myip'])
    # else:
    #     return "dnserr"


if __name__ == "__main__":
    app.run(debug=True)
