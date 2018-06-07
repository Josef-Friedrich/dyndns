import re


class JfErr(Exception):
    pass


def secret(secret):
    secret = str(secret)
    if re.match('^[a-zA-Z0-9]+$', secret) and len(secret) >= 8:
        return secret
    else:
        raise JfErr('The secret must be at least 8 characters long and may '
                    'not contain any non-alpha-numeric characters.')
