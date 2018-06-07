import dns.exception
import dns.name
import dns.query
import dns.resolver
import dns.tsigkeyring
import dns.update
import re


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
        fqdn = '{}.{}'.format(record_name, self._zone)
        fqdn = re.sub('\.+', '.', fqdn)
        return dns.name.from_text(fqdn)

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
        try:
            ip = resolver.query(
                self._build_fqdn(record_name),
                self._convert_record_type(ip_version),
            )
            return str(ip[0])
        except dns.exception.DNSException:
            return ''

    def _set_record(self, new_ip, ip_version=4):
        out = {}
        old_ip = self._resolve(self.record_name, ip_version)
        out['ip_version'] = ip_version
        out['new_ip'] = new_ip
        out['old_ip'] = old_ip
        out['status'] = 'UNCHANGED'

        if new_ip != old_ip:
            fqdn = str(self._build_fqdn(self.record_name))
            rdtype = self._convert_record_type(ip_version)
            self._dns_update.delete(fqdn, rdtype)
            self._dns_update.add(fqdn, 300, rdtype, new_ip)
            dns.query.tcp(self._dns_update, self.nameserver)
            checked_ip = self._resolve(self.record_name, ip_version)
            out['status'] = 'UPDATED'

            if new_ip != checked_ip:
                out['status'] = 'ERROR'

        return out

    def update(self):
        results = []
        if self.ipv4:
            results.append(self._set_record(new_ip=self.ipv4, ip_version=4))
        if self.ipv6:
            results.append(self._set_record(new_ip=self.ipv6, ip_version=6))

        return results
