import dns.name
import dns.query
import dns.update
import dns.tsigkeyring

from flask import Flask
from flask import request
from flask import abort
from flask import Response
from functools import wraps


DOMAIN = 'dyn.example.org'
DNSHOST = 'dns.example.org'

KEYRING = dns.tsigkeyring.from_text({
    'updatekey.': 'reallyrandomsecretdatathatyoucanthavereally'
})

app = Flask(__name__)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'username' and password == 'password'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route("/nic/update")
@requires_auth
def update():
    if 'hostname' not in request.args:
        abort(400)
    if 'myip' not in request.args:
        abort(400)
    hostname = dns.name.from_text(request.args['hostname'])
    domain = dns.name.from_text(DOMAIN)
    particle = hostname.relativize(domain)
    if not hostname.is_subdomain(domain):
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
