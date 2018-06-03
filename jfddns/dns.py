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

    def __init__(self, nameserver, zone, key):
        self.nameserver = nameserver
        self.zone = dns.name.from_text(zone)
        keyring = {}
        keyring[str(self.zone)] = key
        self.keyring = dns.tsigkeyring.from_text(keyring)
        self.dns_update = dns.update.Update(self.zone, keyring=self.keyring)

    def _concatenate(self, record_name):
        return dns.name.from_text('{}.{}'.format(record_name, self.zone))

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
        return str(resolver.query(self._concatenate(record_name),
                                  self._convert_record_type(ip_version))[0])

    def set_record(self, record_name, new_ip, ip_version=4):
        out = {}
        old_ip = self._resolve(record_name, ip_version)
        if new_ip == old_ip:
            out['old_ip'] = old_ip
        else:
            self.dns_update.delete(record_name)
            self.dns_update.add(record_name, 300,
                                self._convert_record_type(ip_version), new_ip)
            dns.query.tcp(self.dns_update, self.nameserver)
            checked_ip = self._resolve(record_name, ip_version)

            if new_ip != checked_ip:
                out['message'] = 'The DNS record couldn’t be updated.'
            else:
                out['new_ip'] = new_ip

        return out
