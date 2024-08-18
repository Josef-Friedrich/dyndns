"""Deal with different kind of names (FQDNs (Fully Qualified Domain Names),
record and zone names)

``record_name`` + ``zone_name`` = ``fqdn``

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dyndns.config import validate_name
from dyndns.exceptions import DnsNameError

if TYPE_CHECKING:
    from dyndns.zones import ZonesCollection


class FullyQualifiedDomainName:
    """
    Stores a FQDN (Fully Qualified Domain Names),
    a zone name and a record along with the TSIG (Transaction SIGnature) key.

    ``record_name`` + ``zone_name`` = ``fqdn``

    :param zones: The ZonesCollection object.
    :param fqdn: The Fully Qualified Domain Name (e. g. ``www.example.com.``).
    :param zone_name: The zone name (e. g. ``example.com.``).
    :param record_name: The name of the resource record (e. g. ``www.``).

    :raises NamesError: If both fqdn and zone_name/record_name are specified.
    :raises NamesError: If record_name is not provided.
    :raises NamesError: If zone_name is not provided.
    """

    fqdn: str
    """The Fully Qualified Domain Name (e. g. ``www.example.com.``)."""

    zone_name: str
    """The zone name (e. g. ``example.com.``)."""

    record_name: str
    """The name of the resource record (e. g. ``www.``)."""

    tsig_key: str
    """The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``)"""

    def __init__(
        self,
        zones: "ZonesCollection",
        fqdn: str | None = None,
        zone_name: str | None = None,
        record_name: str | None = None,
    ) -> None:
        """
        Initialize the ``DomainName`` object.

        :param zones: The ZonesCollection object.
        :param fqdn: The Fully Qualified Domain Name (e. g. ``www.example.com.``).
        :param zone_name: The zone name (e. g. ``example.com.``).
        :param record_name: The name of the resource record (e. g. ``www.``).

        :raises NamesError: If both fqdn and zone_name/record_name are specified.
        :raises NamesError: If record_name is not provided.
        :raises NamesError: If zone_name is not provided.
        """
        if fqdn and zone_name and record_name:
            raise DnsNameError('Specify "fqdn" or "zone_name" and "record_name".')

        if fqdn:
            fqdn = validate_name(fqdn)
            split = zones.split_fqdn(fqdn)
            if split:
                record_name = split[0]
                zone_name = split[1]
            else:
                raise DnsNameError(
                    f"The fully qualified domain name '{fqdn}' could not be split into a record and a zone name."
                )

        if not fqdn and zone_name and record_name:
            record_name = validate_name(record_name)
            zone_name = validate_name(zone_name)
            zone = zones.get_zone(zone_name)
            fqdn = zone.get_fqdn(record_name)

        if not fqdn:
            raise DnsNameError('Value "fqdn" is required.')

        if not record_name:
            raise DnsNameError('Value "record_name" is required.')

        if not zone_name:
            raise DnsNameError('Value "zone_name" is required.')

        self.fqdn = fqdn
        self.zone_name = zone_name
        self.record_name = record_name
        self.tsig_key = zones.get_zone(self.zone_name).tsig_key
