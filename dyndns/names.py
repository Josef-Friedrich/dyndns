"""Deal with different kind of names (FQDNs (Fully Qualified Domain Names),
record and zone names)

``record_name`` + ``zone_name`` = ``fqdn``

"""

# standard imports
import binascii
import re

# third party imports
import dns.name
import dns.tsigkeyring
import dns.tsig
from dyndns.exceptions import NamesError


def validate_hostname(hostname):
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        raise NamesError(
            'The hostname "{}..." is longer than 253 characters.'
            .format(hostname[:10])
        )

    labels = hostname.split(".")

    tld = labels[-1]
    if re.match(r"[0-9]+$", tld):
        raise NamesError(
            'The TLD "{}" of the hostname "{}" must be not all-numeric.'
            .format(tld, hostname)
        )

    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    for label in labels:
        if not allowed.match(label):
            raise NamesError(
                'The label "{}" of the hostname "{}" is invalid.'
                .format(label, hostname)
            )

    return str(dns.name.from_text(hostname))


def validate_tsig_key(tsig_key):
    if not tsig_key:
        raise NamesError('Invalid tsig key: "{}".'.format(tsig_key))
    try:
        dns.tsigkeyring.from_text({'tmp.org.': tsig_key})
        return tsig_key
    except binascii.Error:
        raise NamesError('Invalid tsig key: "{}".'.format(tsig_key))


class Zone:

    def __init__(self, zone_name, tsig_key):
        self.zone_name = validate_hostname(zone_name)
        self.tsig_key = validate_tsig_key(tsig_key)

    def split_fqdn(self, fqdn):
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.
        """
        fqdn = validate_hostname(fqdn)
        record_name = fqdn.replace(self.zone_name, '')
        if record_name and len(record_name) < len(fqdn):
            return (record_name, self.zone_name)
        raise NamesError('FQDN "{}" is not splitable by zone "{}".')

    def build_fqdn(self, record_name):
        record_name = validate_hostname(record_name)
        return record_name + self.zone_name


class Zones:

    def __init__(self, zones_config):
        self.zones = {}
        for zone_config in zones_config:
            zone = Zone(
                zone_name=zone_config['name'],
                tsig_key=zone_config['tsig_key']
            )
            self.zones[zone.zone_name] = zone

    def get_zone_by_name(self, zone_name):
        zone_name = validate_hostname(zone_name)
        if zone_name in self.zones:
            return self.zones[validate_hostname(zone_name)]
        raise NamesError('Unkown zone "{}".'.format(zone_name))

    def split_fqdn(self, fqdn):
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.
        """
        fqdn = validate_hostname(fqdn)
        # To handle subzones (example.com and dyndns.example.com)
        results = {}
        for _, zone in self.zones.items():
            record_name = fqdn.replace(zone.zone_name, '')
            if record_name and len(record_name) < len(fqdn):
                results[len(record_name)] = (record_name, zone.zone_name)
        for key in sorted(results):
            return results[key]
        return False


class Names:

    def __init__(self, zones, fqdn=None, zone_name=None, record_name=None):
        self.fqdn = None
        """The Fully Qualified Domain Name (e. g. ``www.example.com.``)"""

        self.zone_name = None
        """The zone name (e. g. ``example.com.``)"""

        self.record_name = None
        """The name resource record (e. g. ``www.``)"""

        if fqdn and zone_name and record_name:
            raise NamesError('Specify "fqdn" or "zone_name" and '
                             '"record_name".')

        self._zones = zones

        if fqdn:
            self.fqdn = validate_hostname(fqdn)
            split = self._zones.split_fqdn(fqdn)
            if split:
                self.record_name = split[0]
                self.zone_name = split[1]

        if not fqdn and zone_name and record_name:
            self.record_name = validate_hostname(record_name)
            self.zone_name = validate_hostname(zone_name)
            zone = self._zones.get_zone_by_name(self.zone_name)
            self.fqdn = zone.build_fqdn(self.record_name)

        if not self.record_name:
            raise NamesError('Value "record_name" is required.')

        if not self.zone_name:
            raise NamesError('Value "zone_name" is required.')

        self._zone = self._zones.get_zone_by_name(self.zone_name)
        self.tsig_key = self._zone.tsig_key
        """The twig key (e. g. ``tPyvZA==``)"""
