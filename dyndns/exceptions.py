"""A collection of exceptions."""


class DyndnsError(Exception):
    """Base exception of the package ``dyndns``."""


class NamesError(DyndnsError):
    """This error gets thrown by invalid DNS names."""


class IpAddressesError(DyndnsError):
    """This error gets thrown by invalid IP addresses."""


class ConfigurationError(DyndnsError):
    """dyndns configuration error."""


class ParameterError(DyndnsError):
    """Client side parameter error."""


class DNSServerError(DyndnsError):
    """Communicating with the external DNS server."""
