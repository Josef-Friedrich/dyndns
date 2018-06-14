"""A collection of exceptions."""


class JfDDnsError(Exception):
    """Base exception of the package ``jfddns``."""


class NamesError(JfDDnsError):
    """This error gets thrown by invalid DNS names."""


class IpAddressesError(JfDDnsError):
    """This error gets thrown by invalid IP addresses."""


class ConfigurationError(JfDDnsError):
    """jfddns configuration error."""


class ParameterError(JfDDnsError):
    """Client side parameter error."""


class DNSServerError(JfDDnsError):
    """Communicating with the external DNS server."""
