"""Interface for DNS updates."""

# third party imports
import flask

from dyndns.config import get_config
from dyndns.exceptions import \
    ConfigurationError, \
    DNSServerError, \
    IpAddressesError, \
    NamesError, \
    ParameterError
from dyndns.ipaddresses import IpAddresses
from dyndns.log import msg
from dyndns.names import Names
from dyndns.dns import DnsUpdate


def authenticate(secret, config):
    if str(secret) != str(config['secret']):
        raise ParameterError('You specified a wrong secret key.')


def parameter_err(function, exception, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except exception as e:
        raise ParameterError(str(e))


def update_dns_record(secret=None, fqdn=None, zone_name=None, record_name=None,
                      ip_1=None, ip_2=None, ipv4=None, ipv6=None, ttl=None,
                      config=None):
    """
    Update a DNS record.

    :param str secret: A password like secret string. The secret string has to
      be at least 8 characters long and only alphnumeric characters are
      allowed.
    :param str fqdn: The Fully-Qualified Domain Name
      (e. g. ``www.example.com``). If you specify the argument ``fqdn``, you
      don’t have to specify the arguments ``zone_name`` and ``record_name``.
    :param str zone_name: The zone name (e. g. ``example.com``). You have to
      specify the argument ``record_name``.
    :param str record_name: The record name (e. g. ``www``). You have to
      specify the argument ``zone_name``.
    :param str ip_1: A IP address, can be version 4 or version 6.
    :param str ip_2: A second IP address, can be version 4 or version 6. Must
      be a different version than ``ip_1``.
    :param str ipv4: A IP address version 4.
    :param str ipv6: A IP address version 6.
    :param int ttl: Time to live.
    :param dict config: The configuration in the Python dictionary format
      (as returned by the function ``validate_config()``).
    """

    if not config:
        config = get_config()

    zones = config['zones']

    authenticate(secret, config)

    names = parameter_err(Names, NamesError, zones, fqdn=fqdn,
                          zone_name=zone_name, record_name=record_name)
    ipaddresses = parameter_err(IpAddresses, IpAddressesError, ip_1=ip_1,
                                ip_2=ip_2, ipv4=ipv4, ipv6=ipv6,
                                request=flask.request)

    update = DnsUpdate(
        nameserver=config['nameserver'],
        names=names,
        ipaddresses=ipaddresses,
        ttl=ttl,
    )
    results = update.update()

    messages = []
    for result in results:
        message = 'fqdn: {} old_ip: {} new_ip: {}'.format(
            names.fqdn,
            result['old_ip'],
            result['new_ip'],
        )
        messages.append(msg(message, result['status']))

    return ''.join(messages)


def delete_dns_record(secret=None, fqdn=None, config=None):
    if not config:
        config = get_config()
    zones = config['zones']

    authenticate(secret, config)

    names = parameter_err(Names, NamesError, zones, fqdn=fqdn)

    delete = DnsUpdate(
        nameserver=config['nameserver'],
        names=names,
    )

    if delete.delete():
        return msg('Deleted "{}".'.format(names.fqdn), 'UPDATED')
    return msg('Deletion not successful "{}".'.format(names.fqdn),
               'UNCHANGED')


def catch_errors(function, **kwargs):
    try:
        return function(**kwargs)
    except ParameterError as error:
        return msg(str(error), 'PARAMETER_ERROR')
    except ConfigurationError as error:
        return msg(str(error), 'CONFIGURATION_ERROR')
    except DNSServerError as error:
        return msg(str(error), 'DNS_SERVER_ERROR')
