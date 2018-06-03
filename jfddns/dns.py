import dns.name
import dns.query
import dns.resolver
import dns.tsigkeyring
import dns.update


def normalize_dns_name(name):
    return str(dns.name.from_text(name))


def split_fqdn(fqdn, zones):
    """Split hostname into record_name and zone_name
    for example: www.example.com -> www. example.com.
    """
    fqdn = normalize_dns_name(fqdn)
    for zone in zones:
        zone_name = zone['zone']
        zone_name = normalize_dns_name(zone_name)
        record_name = fqdn.replace(zone_name, '')
        if len(record_name) > 0 and len(record_name) < len(fqdn):
            return (record_name, zone_name)


class Zones(object):

    def __init__(self, zones):
        self.zones = []
        for zone in zones:
            _zone = {}
            zone_name = normalize_dns_name(zone['name'])
            _zone[zone_name] = zone['tsig_key']
            self.zones.append(_zone)

    def split_fqdn(self, fqdn):
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.
        """
        fqdn = normalize_dns_name(fqdn)
        for zone in self.zones:
            for zone_name, tsig_key in zone.items():
                record_name = fqdn.replace(zone_name, '')
                if len(record_name) > 0 and len(record_name) < len(fqdn):
                    return (record_name, zone_name)


class DnsUpdate(object):
    """
    Update the DNS server
    """

    def __init__(self, nameserver, zone_name, tsig_key,
                 record_name=None, ipv4=None, ipv6=None):

        self.ipv4 = ipv4  #: The ipv4 address
        self.ipv6 = ipv6  #: The ipv6 address
        self.nameserver = nameserver   #: The nameserver
        self.record_name = record_name  #: The record name
        self.tsig_key = tsig_key  #: The tsig key
        self.zone_name = zone_name  #: The zone name

        self._zone = dns.name.from_text(zone_name)
        self._tsigkeyring = self._build_tsigkeyring(self._zone, self.tsig_key)
        self._dns_update = dns.update.Update(self._zone,
                                             keyring=self._tsigkeyring)

    @staticmethod
    def _build_tsigkeyring(zone, tsig_key):
        """
        :param zone: A zone name object
        :type dns.name.Name: A instance of a dns.name.Name class
        :param str tsig_key: A TSIG key
        """
        keyring = {}
        keyring[str(zone)] = tsig_key
        return dns.tsigkeyring.from_text(keyring)

    def _build_fqdn(self, record_name):
        return dns.name.from_text('{}.{}'.format(record_name, self._zone))

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
        return str(resolver.query(self._build_fqdn(record_name),
                                  self._convert_record_type(ip_version))[0])

    def _set_record(self, new_ip, ip_version=4):
        out = {}
        old_ip = self._resolve(self.record_name, ip_version)
        if new_ip == old_ip:
            out['old_ip'] = old_ip
        else:
            self._dns_update.delete(self.record_name)
            self._dns_update.add(self.record_name, 300,
                                 self._convert_record_type(ip_version), new_ip)
            dns.query.tcp(self._dns_update, self.nameserver)
            checked_ip = self._resolve(self.record_name, ip_version)

            if new_ip != checked_ip:
                out['message'] = 'The DNS record couldn’t be updated.'
            else:
                out['new_ip'] = new_ip

        return out

    def update(self):
        results = []
        if self.ipv4:
            results.append(self._set_record(new_ip=self.ipv4, ip_version=4))
        if self.ipv6:
            results.append(self._set_record(new_ip=self.ipv6, ip_version=6))
