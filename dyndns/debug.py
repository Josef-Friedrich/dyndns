#! /usr/bin/env python

import random
import string

import dns.query
import dns.tsig
import dns.tsigkeyring
import dns.update
from dns.resolver import Answer, Resolver

from dyndns.config import get_config

NAME_SERVER = "127.0.0.1"

DEBUG_RECORD_NAME = "abcdef"


resolver = Resolver()
resolver.nameservers = [NAME_SERVER]


config = get_config()


keyring = dns.tsigkeyring.from_text(
    {config["zones"][0]["name"]: config["zones"][0]["tsig_key"]}
)


random_txt = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def init_update_object() -> dns.update.Update:
    return dns.update.Update(
        config["zones"][0]["name"], keyring=keyring, keyalgorithm=dns.tsig.HMAC_SHA512
    )


def delete(record_name: str, rdtype: str = "A") -> None:
    update = init_update_object()
    update.delete(record_name, rdtype)
    dns.query.tcp(update, NAME_SERVER)


def add(record_name: str, ttl: int, rdtype: str, content: str) -> None:
    update = init_update_object()
    update.add(record_name, 300, rdtype, content)
    dns.query.tcp(update, NAME_SERVER)


def resolve(record_name: str, rdtype: str):
    answers: Answer = resolver.resolve(
        record_name + "." + config["zones"][0]["name"], rdtype
    )
    for rdata in answers:
        return rdata


delete(DEBUG_RECORD_NAME, "TXT")
add(DEBUG_RECORD_NAME, 300, "TXT", random_txt)

result = resolve(DEBUG_RECORD_NAME, "TXT")

print(random_txt)
print(result.strings[0])

if result.strings[0].decode() == random_txt:
    print("DNS is working!")
else:
    raise Exception("DNS error")

delete(DEBUG_RECORD_NAME, "TXT")
