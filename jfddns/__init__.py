
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

KEYRING = dns.tsigkeyring.from_text({
    'updatekey.': '+Vzj6Uu4JeW6EnWqrm2OlT3uBx7weGK5upD+qB+MuiavbXmqitSOXImAOp+ddSODFwzyK7VD6NU5iIgRrc48hg=='
})

app = Flask(__name__)

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
    update = dns.update.Update(DOMAIN, keyring=KEYRING)
    update.delete(str(particle))
    update.add(str(particle), 600, 'a', str(request.args['myip']))
    response = dns.query.tcp(update, DNSHOST)
    if response.rcode() == 0:
        return "good "+str(request.args['myip'])
    else:
        return "dnserr"

if __name__ == "__main__":
    app.run(debug=True)
