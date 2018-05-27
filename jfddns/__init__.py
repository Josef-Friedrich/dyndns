
import yaml
from flask import abort
from flask import Flask
from flask import request
from flask import Response
from functools import wraps
import dns.name
import dns.query
import dns.tsigkeyring
import dns.update

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

    def set_record(self, record, ip):
        self.dns_update.delete(record)
        self.dns_update.add(record, 300, 'A', ip)
        dns.query.tcp(self.dns_update, self.nameserver)


def usage():
    return 'Usage: secret=<secret>&zone=<zone>&record=<record>&ipv6=<ipv6>&ipv4=<ipv4>'


@app.route("/")
def update():
    if 'record' not in request.args:
        return usage()
    if 'ipv4' not in request.args:
        abort(400)
    record = dns.name.from_text(request.args['record'])
    print(record)
    domain = dns.name.from_text(DOMAIN)
    particle = record.relativize(domain)
    if not record.is_subdomain(domain):
        return 'nohost'

    if response.rcode() == 0:
        return "good "+str(request.args['myip'])
    else:
        return "dnserr"


if __name__ == "__main__":
    app.run(debug=True)
