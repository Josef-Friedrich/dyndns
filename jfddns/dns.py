"""Query the DSN server using the package“dnspython”."""

from jfddns.exceptions import DNSServerError
import dns.exception
import dns.name
import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring
import dns.update


class DnsUpdate(object):
    """
    Update the DNS server
    """

    def __init__(self, nameserver, names, ipaddresses):
        self.nameserver = nameserver   #: The nameserver
        self.names = names
        self.ipaddresses = ipaddresses

        self._tsigkeyring = self._build_tsigkeyring(
            self.names.zone_name,
            self.names.tsig_key,
        )
        self._dns_update = dns.update.Update(self.names.zone_name,
                                             keyring=self._tsigkeyring)

    @staticmethod
    def _build_tsigkeyring(zone_name, tsig_key):
        """
        :param zone: A zone name object
        :type dns.name.Name: A instance of a dns.name.Name class
        :param str tsig_key: A TSIG key
        """
        keyring = {}
        keyring[zone_name] = tsig_key
        return dns.tsigkeyring.from_text(keyring)

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
                self.names.fqdn,
                self._convert_record_type(ip_version),
            )
            return str(ip[0])
        except dns.exception.DNSException:
            return ''

    def _set_record(self, new_ip, ip_version=4):
        out = {}
        old_ip = self._resolve(self.names.record_name, ip_version)
        out['ip_version'] = ip_version
        out['new_ip'] = new_ip
        out['old_ip'] = old_ip
        out['status'] = 'UNCHANGED'

        if new_ip != old_ip:
            rdtype = self._convert_record_type(ip_version)
            self._dns_update.delete(self.names.fqdn, rdtype)
            self._dns_update.add(self.names.fqdn, 300, rdtype, new_ip)
            try:
                dns.query.tcp(self._dns_update, where=self.nameserver,
                              timeout=5)
            except dns.tsig.PeerBadKey as error:
                raise DNSServerError('The peer "{}" didn\'t know the tsig key '
                                     'we used for the zone "{}".'.format(
                                        self.nameserver,
                                        self.names.zone_name,
                                     ))
            except dns.exception.Timeout as error:
                raise DNSServerError('The DNS operation to the nameserver '
                                     '"{}" timed out.'.format(self.nameserver))
            checked_ip = self._resolve(self.names.record_name, ip_version)
            out['status'] = 'UPDATED'

            if new_ip != checked_ip:
                out['status'] = 'DNS_SERVER_ERROR'

        return out

    def update(self):
        results = []
        if self.ipaddresses.ipv4:
            results.append(self._set_record(new_ip=self.ipaddresses.ipv4,
                           ip_version=4))
        if self.ipaddresses.ipv6:
            results.append(self._set_record(new_ip=self.ipaddresses.ipv6,
                           ip_version=6))

        return results
