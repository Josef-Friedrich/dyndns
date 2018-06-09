class JfErr(Exception):
    pass


class JfDDnsError(Exception):
    """Base exception of the package ``jfddns``."""


class ConfigurationError(JfDDnsError):
    """Server side configuration error."""


class ParameterError(JfDDnsError):
    """Client side parameter error."""
