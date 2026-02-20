"""A collection of exceptions."""

from __future__ import annotations

from dyndns.log import LogLevel


class DyndnsError(Exception):
    """Base exception of the package ``dyndns``."""

    status_code: int = 452
    """
    https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    """

    log_level: LogLevel


class DnsNameError(DyndnsError):
    """This error gets thrown by invalid DNS names."""

    log_level = LogLevel.DNS_NAME_ERROR

    status_code = 453


class IpAddressesError(DyndnsError):
    """This error gets thrown by invalid IP addresses."""

    log_level = LogLevel.IP_ADDRESS_ERROR

    status_code = 454


class ConfigurationError(DyndnsError):
    """An error if ``dyndns`` has been configured incorrectly.
    This mainly affects the configuration file in YAML format
    (``/etc/dyndns.yml`` oder ``~/.dyndns.yml``)."""

    log_level = LogLevel.CONFIGURATION_ERROR

    status_code = 455


class ParameterError(DyndnsError):
    """Client side parameter error."""

    log_level = LogLevel.PARAMETER_ERROR

    status_code = 456


class CheckError(DyndnsError):
    """The check failed."""

    log_level = LogLevel.CHECK_ERROR

    status_code = 457


class DNSServerError(DyndnsError):
    """Communicating with the external DNS server."""

    log_level = LogLevel.DNS_SERVER_ERROR

    status_code = 512
