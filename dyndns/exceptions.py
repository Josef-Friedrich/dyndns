"""A collection of exceptions."""


class dyndnsError(Exception):
    """Base exception of the package ``dyndns``."""


class NamesError(dyndnsError):
    """This error gets thrown by invalid DNS names."""


class IpAddressesError(dyndnsError):
    """This error gets thrown by invalid IP addresses."""


class ConfigurationError(dyndnsError):
    """dyndns configuration error."""


class ParameterError(dyndnsError):
    """Client side parameter error."""


class DNSServerError(dyndnsError):
    """Communicating with the external DNS server."""
