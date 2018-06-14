class JfErr(Exception):
    pass


class JfDDnsError(Exception):
    """Base exception of the package ``jfddns``."""


class NamesError(JfDDnsError):
    """This error gets thrown by invalid DNS names."""


class ConfigurationError(JfDDnsError):
    """Server side configuration error."""


class ParameterError(JfDDnsError):
    """Client side parameter error."""
