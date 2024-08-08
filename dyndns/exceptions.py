"""A collection of exceptions."""

from __future__ import annotations


class DyndnsError(Exception):
    """Base exception of the package ``dyndns``."""

    status_code = 452
    """
    https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    """


class NamesError(DyndnsError):
    """This error gets thrown by invalid DNS names."""

    status_code = 453


class IpAddressesError(DyndnsError):
    """This error gets thrown by invalid IP addresses."""

    status_code = 454


class ConfigurationError(DyndnsError):
    """dyndns configuration error."""

    status_code = 455


class ParameterError(DyndnsError):
    """Client side parameter error."""

    status_code = 456


class DNSServerError(DyndnsError):
    """Communicating with the external DNS server."""

    status_code = 512
