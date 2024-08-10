"""A collection of exceptions."""

from __future__ import annotations

from dyndns.log_ng import LogLevel


class DyndnsError(Exception):
    """Base exception of the package ``dyndns``."""

    status_code: int = 452
    """
    https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    """

    log_level: LogLevel


class DnsNameError(DyndnsError):
    """This error gets thrown by invalid DNS names."""

    status_code = 453

    log_level = LogLevel.DNS_NAME_ERROR


class IpAddressesError(DyndnsError):
    """This error gets thrown by invalid IP addresses."""

    status_code = 454


class ConfigurationError(DyndnsError):
    """dyndns configuration error."""

    status_code = 455


class ParameterError(DyndnsError):
    """Client side parameter error."""

    status_code = 456


class CheckError(DyndnsError):
    """The check failed."""

    status_code = 457


class DNSServerError(DyndnsError):
    """Communicating with the external DNS server."""

    status_code = 512
