"""Load and validate the configuration."""

# standard imports
import os
import re
import yaml

# third party imports
from dyndns.names import Zones, validate_hostname
from dyndns.exceptions import ConfigurationError, NamesError, IpAddressesError
from dyndns.ipaddresses import validate as validate_ip


def load_config(config_file=None):
    config_files = []
    if config_file:
        config_files.append(config_file)
    if 'dyndns_CONFIG_FILE' in os.environ:
        config_files.append(os.environ['dyndns_CONFIG_FILE'])
    config_files.append(os.path.join(os.getcwd(), '.dyndns.yml'))
    config_files.append('/etc/dyndns.yml')

    for _config_file in config_files:
        if os.path.exists(_config_file):
            config_file = _config_file
            break

    if not config_file:
        raise ConfigurationError('The configuration file could not be found.')

    stream = open(config_file, 'r')
    config = yaml.safe_load(stream)
    stream.close()
    return config


def validate_secret(secret):
    secret = str(secret)
    if re.match('^[a-zA-Z0-9]+$', secret) and len(secret) >= 8:
        return secret
    raise ConfigurationError('The secret must be at least 8 characters '
                             'long and may not contain any '
                             'non-alpha-numeric characters.')


def validate_config(config=None):

    if not config:
        try:
            config = load_config()
        except IOError:
            raise ConfigurationError('The configuration file could not be '
                                     'found.')
        except yaml.error.YAMLError:
            raise ConfigurationError('The configuration file is in a invalid '
                                     'YAML format.')

    if 'secret' not in config:
        raise ConfigurationError('Your configuration must have a "secret" '
                                 'key, for example: "secret: VDEdxeTKH"')

    config['secret'] = validate_secret(config['secret'])

    if 'nameserver' not in config:
        raise ConfigurationError('Your configuration must have a "nameserver" '
                                 'key, for example: "nameserver: 127.0.0.1"')

    try:
        validate_ip(config['nameserver'])
    except IpAddressesError:
        msg = 'The "nameserver" entry in your configuration is not a valid ' \
              'IP address: "{}".'.format(config['nameserver'])
        raise ConfigurationError(msg)

    if 'dyndns_domain' in config:
        try:
            validate_hostname(config['dyndns_domain'])
        except NamesError as error:
            raise ConfigurationError(str(error))

    if 'zones' not in config:
        raise ConfigurationError('Your configuration must have a "zones" key.')

    if not isinstance(config['zones'], (list,)):
        raise ConfigurationError('Your "zones" key must contain a list of '
                                 'zones.')

    if not config['zones']:
        raise ConfigurationError('You must have at least one zone configured, '
                                 'for example: "- name: example.com" and '
                                 '"tsig_key: tPyvZA=="')

    for zone in config['zones']:
        if 'name' not in zone:
            raise ConfigurationError('Your zone dictionary must contain a key '
                                     '"name"')

        if 'tsig_key' not in zone:
            raise ConfigurationError('Your zone dictionary must contain a key '
                                     '"tsig_key"')

    try:
        config['zones'] = Zones(config['zones'])
    except NamesError as error:
        raise ConfigurationError(str(error))

    return config


def get_config(config_file=None):
    return validate_config(load_config(config_file))
