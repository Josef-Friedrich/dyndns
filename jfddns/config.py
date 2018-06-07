from jfddns import validate
from jfddns.validate import JfErr
from jfddns.names import Zones
import os
import yaml


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


def validate_config(config=None):

    ##
    # config
    ##

    if not config:
        try:
            config = load_config()
        except IOError:
            raise JfErr('The configuration file could not be found.')
        except yaml.error.YAMLError:
            raise JfErr('The configuration file is in a invalid YAML format.')

    if not config:
        raise JfErr('The configuration file could not be found.')

    if 'secret' not in config:
        raise JfErr('Your configuration must have a "secret" key, '
                    'for example: "secret: VDEdxeTKH"')

    config['secret'] = validate.secret(config['secret'])

    if 'nameserver' not in config:
        raise JfErr('Your configuration must have a "nameserver" key, '
                    'for example: "nameserver: 127.0.0.1"')

    if 'zones' not in config:
        raise JfErr('Your configuration must have a "zones" key.')

    if not isinstance(config['zones'], (list,)):
        raise JfErr('Your "zones" key must contain a list of zones.')

    if len(config['zones']) < 1:
        raise JfErr('You must have at least one zone configured, for example:'
                    '"- name: example.com" and "tsig_key: tPyvZA=="')

    for zone in config['zones']:
        if 'name' not in zone:
            raise JfErr('Your zone dictionary must contain a key "name"')

        if 'tsig_key' not in zone:
            raise JfErr('Your zone dictionary must contain a key "tsig_key"')

    config['zones'] = Zones(config['zones'])

    return config
